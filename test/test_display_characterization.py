"""Golden-master characterization tests for ``query_app.py``'s display/result layer.

The table-formatting and result-orchestration functions live *inside* the marimo
notebook (``query_app.py``), not in ``utils/`` — they can't be packaged/imported
for the WASM build, so there's nothing to ``import`` here. Instead we load the
notebook's cell bodies via AST into a namespace (stubbing marimo) and drive the
real result-orchestration cell across every district and a sample of uses.

This is a *content* golden master: it captures each view's columns, shape, dtypes,
styling, and a hash of the full table content, and compares against a committed
baseline. Any change to what a user would see — column order, which columns show,
or the actual result rows — fails the test. Data refreshes are rare and deliberate;
when the source CSVs are intentionally updated, regenerate the baseline with:

    UPDATE_DISPLAY_BASELINE=1 python -m pytest test/test_display_characterization.py

and review the git diff of ``test/data/display_baseline.json``.
"""

import ast
import hashlib
import json
import os
import pathlib
from unittest.mock import MagicMock

import pandas as pd
import polars as pl
import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTEBOOK = REPO_ROOT / "query_app.py"
BASELINE_PATH = pathlib.Path(__file__).resolve().parent / "data" / "display_baseline.json"
ORCH_MARKER = "by_use_name_result ="


class _CapturedTable:
    """Stand-in for mo.ui.table that records the DataFrame it was handed."""

    def __init__(self, data, **kwargs):
        self.data = data
        self.kwargs = kwargs


def _is_cell(node: ast.AST) -> bool:
    return isinstance(node, ast.FunctionDef) and any(
        (isinstance(d, ast.Attribute) and d.attr == "cell")
        or (
            isinstance(d, ast.Call)
            and isinstance(d.func, ast.Attribute)
            and d.func.attr == "cell"
        )
        for d in node.decorator_list
    )


def _build_namespace():
    """Exec every ``@app.cell`` body into one namespace; return it plus the
    orchestration cell's source (which needs per-call selection inputs)."""
    mo = MagicMock(name="mo")
    mo.ui.table.side_effect = lambda data, **kw: _CapturedTable(data, **kw)
    mo.ui.tabs.side_effect = lambda d: d
    mo.vstack.side_effect = lambda items: list(items)
    mo.notebook_location.return_value = REPO_ROOT
    ns = {"pd": pd, "pl": pl, "mo": mo, "pyarrow": MagicMock()}

    tree = ast.parse(NOTEBOOK.read_text())
    orch_src = None
    cell_sources = []
    for node in tree.body:
        if not _is_cell(node):
            continue
        body = [n for n in node.body if not isinstance(n, ast.Return)]
        code = ast.unparse(ast.Module(body=body, type_ignores=[]))
        if ORCH_MARKER in code:
            orch_src = code
        else:
            cell_sources.append(code)
    assert orch_src is not None, "could not locate the result-orchestration cell"

    # marimo runs cells in dataflow order, not file order; exec in repeated passes
    # so forward references (a load cell using a later-defined helper) resolve.
    pending = list(cell_sources)
    for _ in range(len(cell_sources)):
        still_failing = []
        for code in pending:
            try:
                exec(code, ns)
            except Exception:
                still_failing.append(code)  # UI-only cells stay failed; that's fine
        if len(still_failing) == len(pending):
            break
        pending = still_failing
    return ns, orch_src


def _snapshot(result):
    """Normalize a result-layer value into a JSON-able, diff-friendly snapshot."""
    if isinstance(result, _CapturedTable):
        df = result.data
        style = result.kwargs.get("style_cell")
        return {
            "kind": "table",
            "columns": list(df.columns),
            "shape": list(df.shape),
            "dtypes": [str(t) for t in df.dtypes],
            "style_cell": getattr(style, "__name__", str(style)),
            "content_sha": hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()[:16],
        }
    if isinstance(result, str):
        return {"kind": "message", "text": result}
    if result is None:
        return {"kind": "none"}
    return {"kind": "other", "repr": repr(result)[:120]}


def _capture_all(ns, orch_src):
    """Drive the real orchestration cell across all districts + a use sample."""

    def run(district, use, tab):
        local = dict(ns)
        local["selected_district"] = district
        local["selected_use_name"] = use
        local["tab_use_type"] = MagicMock(value=tab)
        exec(orch_src, local)
        return local

    uses_min = ns["uses_by_zoning_district_minimal"]
    addressed = ns["addressed_naics_titles"]
    captures = {}

    for d in sorted(uses_min["Zoning District"].dropna().unique()):
        result = run(d, None, "Expanded terms")
        captures[f"district::{d}::expanded"] = _snapshot(result["by_district_result_table"])
        captures[f"district::{d}::zr_only"] = _snapshot(result["by_district_result_table_zr_only"])

    zr_names = sorted(
        uses_min[~uses_min["Use Name"].astype(str).str.contains("*", regex=False)]["Use Name"]
        .dropna()
        .unique()
    )
    for name in zr_names[:: max(1, len(zr_names) // 6)][:6]:
        captures[f"zr_use::{name}"] = _snapshot(run(None, name, "Zoning Resolution terms")["by_use_name_result"])

    naics_titles = sorted(addressed["NAICS Title"].dropna().unique())
    expanded = ["Solar cells manufacturing"] + naics_titles[:: max(1, len(naics_titles) // 7)][:7]
    for name in dict.fromkeys(expanded):
        captures[f"naics_use::{name}"] = _snapshot(run(None, name, "Expanded terms")["by_use_name_result"])

    return captures


@pytest.fixture(scope="module")
def notebook():
    ns, orch_src = _build_namespace()
    return {"ns": ns, "orch_src": orch_src}


def test_display_matches_golden_baseline(notebook):
    captures = _capture_all(notebook["ns"], notebook["orch_src"])

    if os.environ.get("UPDATE_DISPLAY_BASELINE"):
        BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_PATH.write_text(json.dumps(captures, indent=2, sort_keys=True) + "\n")
        pytest.skip(f"baseline regenerated ({len(captures)} captures) -> {BASELINE_PATH}")

    assert BASELINE_PATH.exists(), (
        f"missing baseline {BASELINE_PATH}; regenerate with UPDATE_DISPLAY_BASELINE=1"
    )
    baseline = json.loads(BASELINE_PATH.read_text())
    changed = sorted(k for k in set(baseline) | set(captures) if baseline.get(k) != captures.get(k))
    detail = "\n".join(
        f"  {k}\n    baseline: {baseline.get(k)}\n    current : {captures.get(k)}" for k in changed[:15]
    )
    assert not changed, (
        f"{len(changed)} display capture(s) changed vs baseline. If a deliberate data "
        f"refresh or intended change, regenerate with UPDATE_DISPLAY_BASELINE=1 and review "
        f"the diff.\n{detail}"
    )


def test_empty_table_degrades_to_message_not_raise(notebook):
    format_ui_table = notebook["ns"]["format_ui_table"]
    out = format_ui_table(pd.DataFrame(columns=["Is it Allowed?"]))
    assert isinstance(out, str)  # graceful message, not a raise or an empty table


def test_no_input_crashes_across_districts_and_zr_uses(notebook):
    ns, orch_src = notebook["ns"], notebook["orch_src"]

    def run(district, use, tab):
        local = dict(ns)
        local["selected_district"] = district
        local["selected_use_name"] = use
        local["tab_use_type"] = MagicMock(value=tab)
        exec(orch_src, local)

    uses_min = ns["uses_by_zoning_district_minimal"]
    for d in sorted(uses_min["Zoning District"].dropna().unique()):
        run(d, None, "Expanded terms")
    zr_names = sorted(
        uses_min[~uses_min["Use Name"].astype(str).str.contains("*", regex=False)]["Use Name"]
        .dropna()
        .unique()
    )
    for name in zr_names:
        run(None, name, "Zoning Resolution terms")

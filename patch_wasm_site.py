#!/usr/bin/env python3
"""Post-process the marimo WASM export before serving/deploying it.

Currently: disable browser notifications. marimo's frontend fires a browser
Notification ("Execution completed …" / "Execution failed …") when a run finishes
while the tab is backgrounded, and prompts for notification permission on first
interaction. For a public read-only app that's confusing UX, and there is no
marimo config option to turn it off. The frontend guards the whole thing on
``!("Notification" in window)``, so we remove the Notification API before marimo's
bundle loads.

``marimo export`` rewrites ``index.html`` on every build, so this must run after
each export (see build_site.sh, which chains the two).

Usage:
    python3 patch_wasm_site.py [SITE_DIR]   # default: _site_directory
"""

import sys
from pathlib import Path

_MARKER = "data-disable-notifications"
_SNIPPET = (
    f"<script {_MARKER}>"
    "try{delete window.Notification}catch(e){window.Notification=undefined}"
    "</script>"
)


def patch(site_dir: str = "_site_directory") -> None:
    index = Path(site_dir) / "index.html"
    if not index.exists():
        raise SystemExit(f"error: {index} not found — run the marimo export first")
    html = index.read_text()
    if _MARKER in html:
        print(f"already patched: {index}")
        return
    if "<head>" not in html:
        raise SystemExit(f"error: no <head> found in {index}; cannot inject")
    # Inject immediately after <head> so it runs before marimo's scripts.
    index.write_text(html.replace("<head>", "<head>" + _SNIPPET, 1))
    print(f"patched (disabled browser notifications): {index}")


if __name__ == "__main__":
    patch(sys.argv[1] if len(sys.argv) > 1 else "_site_directory")

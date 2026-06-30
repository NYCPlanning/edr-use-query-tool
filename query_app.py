# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo==0.19.4",
#     "pandas==2.3.3",
#     "polars==1.37.1",
#     "pyarrow==22.0.0",
# ]
# ///

import marimo

__generated_with = "0.23.11"
app = marimo.App(
    width="medium",
    app_title="Land Use Lookup",
    css_file="public/custom.css",
)

with app.setup:
    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.Html("""
    <header class="site-header">
        <img src="public/img/dcp-logo.svg" alt="NYC Planning logo" style="width: 96px; height: auto;" />
        <span style="
            font-family: 'Public Sans', sans-serif;
            font-weight: 800;
            font-size: 24px;
            line-height: 24px;
            color: #000000;
        ">Land Use Lookup Tool</span>
    </header>
    """)
    return


@app.cell
def _():
    import pandas as pd
    import polars as pl
    import pyarrow  # to force install in WASM notebook

    # pandas 3.0 defaults string columns to a pyarrow-backed ``str`` dtype. Under
    # Pyodide/WASM those Arrow buffers are read-only, which breaks pandas' merge
    # factorizer (``ValueError: putmask: output array is read-only``) — the table
    # vanishes for any use whose lookup hits a merge. Opting back out of the new
    # string dtype keeps strings as plain numpy ``object`` everywhere (including
    # the ``astype(str)`` calls in the explode helpers), so every merge uses the
    # read-only-safe object path. Guarded because the option may not exist in the
    # exact pandas build Pyodide ships. See to_pandas_writable() for the polars
    # half of this fix.
    try:
        pd.options.future.infer_string = False
    except Exception:
        pass

    # Using mo.notebook_location() to access data both locally and when running via WebAssembly (e.g. hosted on GitHub Pages)
    SOURCE_DATA_DIRECTORY = mo.notebook_location() / "public" / "data"

    def to_pandas_writable(polars_df):
        """Convert a polars DataFrame to pandas with numpy-backed string columns.

        ``polars.to_pandas()`` builds pyarrow-backed columns directly, so it
        ignores the ``future.infer_string`` opt-out above and still yields Arrow
        ``str`` columns. Under Pyodide/WASM those Arrow buffers are read-only and
        break pandas' merge factorizer. Re-materializing the string columns as
        numpy ``object`` arrays gives every downstream merge read-only-safe join
        keys. (Behavior is identical locally, where the buffers are writable.)
        """
        pandas_df = polars_df.to_pandas()
        string_columns = {
            column: object
            for column in pandas_df.columns
            if str(pandas_df[column].dtype) in ("object", "str")
        }
        return pandas_df.astype(string_columns)

    return SOURCE_DATA_DIRECTORY, pd, pl, to_pandas_writable


@app.cell(hide_code=True)
def _():
    mo.Html("""
    <h1 style="
        font-family: 'Public Sans', sans-serif;
        font-weight: 800;
        font-size: 36px;
        line-height: 42px;
        color: #063793;
        margin: 0;
    ">From laundromats to bike shops, find out what uses zoning allows on different lots across New York City.</h1>
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    The Land Use Lookup uses the New York City [Zoning Resolution](https://zoningresolution.planning.nyc.gov/) and the [North American Industry Classification System](https://www.census.gov/naics/?99967) (NAICS) to identify permitted uses.

    Using the tool, you can:
    """)
    return


@app.cell
def _(user_accordion_search):
    user_accordion_search
    return


@app.cell
def _(user_accordion_instructions):
    user_accordion_instructions
    return


@app.cell
def _(user_accordion_view_all):
    user_accordion_view_all
    return


@app.cell
def _():
    # build UI components
    return


@app.cell
def _(addressed_naics_titles, uses_by_zoning_district_minimal):
    dropdown_districts = mo.ui.dropdown(
        uses_by_zoning_district_minimal["Zoning District"],
        label="Zoning District: ",
        searchable=True,
    )
    zr_use_names = uses_by_zoning_district_minimal[
        ~uses_by_zoning_district_minimal["Use Name"]
        .astype(str)
        .str.contains("*", regex=False)
    ]["Use Name"]
    dropdown_zr_uses = mo.ui.dropdown(
        zr_use_names,
        label="Use Name: ",
        searchable=True,
    )
    expanded_use_names = (
        addressed_naics_titles["NAICS Title"].tolist()
        + uses_by_zoning_district_minimal["Use Name"].tolist()
    )
    dropdown_expanded_uses = mo.ui.dropdown(
        sorted(expanded_use_names),
        label="Use Name: ",
        searchable=True,
    )
    tab_use_type = mo.ui.tabs(
        {
            "Zoning Resolution terms": dropdown_zr_uses,
            "Expanded terms": dropdown_expanded_uses,
        }
    )
    return (
        dropdown_districts,
        dropdown_expanded_uses,
        dropdown_zr_uses,
        tab_use_type,
    )


@app.cell
def _(
    dropdown_districts,
    dropdown_expanded_uses,
    dropdown_zr_uses,
    tab_use_type,
):
    selected_district = dropdown_districts.value

    selected_use_name = (
        dropdown_zr_uses.value
        if tab_use_type.value == "Zoning Resolution terms"
        else dropdown_expanded_uses.value
    )
    return selected_district, selected_use_name


@app.cell
def _():
    query_by_district_intro = (
        "**Select a zoning district to see a full list of allowed uses.**"
    )

    query_by_district_note = '_Note: "Expanded terms" include uses named in the Zoning Resolution, affiliated NAICS indices, and select uses manually added by DCP staff for user convenience, denoted by an asterisk (*). Any term defined in the [Zoning Resolution Glossary](https://zr.planning.nyc.gov/article-i/chapter-2#12-10) is denoted by a pound symbol (#). See the Use Notes column for more information on individual uses._'
    return query_by_district_intro, query_by_district_note


@app.cell
def _():
    query_by_use_intro = "**Select a Zoning Resolution use name or from an expanded list of uses that includes NAICS Indexes to see where it's allowed.**"

    query_by_use_note = '_Note: "Expanded terms" include uses named in the Zoning Resolution, affiliated NAICS indices, and select uses manually added by DCP staff for user convenience, denoted by an asterisk (*). Any term defined in the [Zoning Resolution Glossary](https://zr.planning.nyc.gov/article-i/chapter-2#12-10) is denoted by a pound symbol (#). See the Use Notes column for more information on individual uses._'
    return query_by_use_intro, query_by_use_note


@app.cell
def _():
    _disclaimer = mo.md(r"""
    **Disclaimer**: _The Land Use Lookup provides an overview of the use allowances and zoning rules and regulations of New York City and is not intended to serve as a substitute for the actual regulations which are to be found in the Zoning Resolution of the City of New York, available at [zr.planning.nyc.gov](https://zr.planning.nyc.gov). The City disclaims any liability for errors that may be contained herein and shall not be responsible for any damages, consequential or actual, arising out of or in connection with the use of this information._

    _Users should prioritize the language of the Zoning Resolution over associated NAICS index names when considering applicability. Some commercial uses (e.g., agriculture, offices, health care facilities) do not have affiliated NAICS codes specified in the Zoning Resolution, though may align with unlisted NAICS codes and indices._

    _Note that some non-conforming uses exist in the city, particularly where sites pre-date zoning. There are other policies that govern siting and use allowances in addition to zoning. Contact DCP's Zoning Help Desk at 212-720-3291 with site-specific use allowance inquiries._
    """)
    mo.Html(f'<div class="disclaimer">{_disclaimer.text}</div>')
    return


@app.cell
def _(pd):
    _PARKLAND = {
        50: "#DDEFDF",
        100: "#BCDFC0",
        200: "#9ACFA0",
        300: "#79BF81",
        400: "#57AF61",
        500: "#36A042",
        600: "#2D8537",
        700: "#246A2C",
        800: "#1B5021",
        900: "#123516",
        1000: "#091A0B",
    }  # green
    _FIRE_HYDRANT = {
        50: "#FFD4D5",
        100: "#FFAAAB",
        200: "#FF7F81",
        300: "#FF5557",
        400: "#FF2A2D",
        500: "#FF0004",
        600: "#D40003",
        700: "#AA0002",
        800: "#7F0002",
        900: "#550001",
        1000: "#2A0000",
    }  # red
    _METROCARD = {
        50: "#FFF7D9",
        100: "#FFF0B3",
        200: "#FFE88D",
        300: "#FFE167",
        400: "#FFD941",
        500: "#FFD21C",
        600: "#D4AF17",
        700: "#AA8C12",
        800: "#7F690E",
        900: "#554609",
        1000: "#2A2304",
    }  # yellow

    # Temporary knob: set to one of 50, 100, 200, ... 1000 and re-run this cell to
    # shift all three "Is it Allowed?" colors together while picking a set.
    _SHADE = 50

    def _style_is_allowed(_row_id, column_name, value):
        if column_name != "Is it Allowed?":
            return {}
        if value == "Yes":
            return {"backgroundColor": _PARKLAND[_SHADE]}
        if value == "No":
            return {"backgroundColor": _FIRE_HYDRANT[_SHADE]}
        return {"backgroundColor": _METROCARD[_SHADE]}

    def format_ui_table(
        data: pd.DataFrame,
        could_be_empty: bool = False,
        style_cell=_style_is_allowed,
    ):
        if could_be_empty and data.empty:
            # this is only the case when a NAICS Index is not addressed in the ZR
            return "The chosen NAICS Index is not explicitly addressed in the Zoning Resolution. Try an alternative/broader term or search by a Zoning Resolution use."

        if data.empty:
            raise ValueError("Data for a UI table is empty but shouldn't be.")

        return mo.ui.table(
            data,
            page_size=25,
            selection=None,
            show_data_types=False,
            style_cell=style_cell,
        )

    # Canonical left-to-right column order shared by all result tables, so the
    # "Search by use" tabs stay consistent with the by-district view (conditions
    # sit just right of "Is it Allowed?" instead of being pushed to the far right).
    _COLUMN_ORDER = [
        "Zoning District",
        "Is it Allowed?",
        "Special Permit",
        "Size Restrictions",
        "Additional Conditions",
        "Open Use Allowances",
        "Limitations",
        "Use Notes",
        "Use Group",
        "Use Category",
        "Zoning Resolution Use Name",
        "NAICS Index Use Name",
        "NAICS Code",
    ]

    def _order_table_columns(data: pd.DataFrame) -> pd.DataFrame:
        # Keep known columns in canonical order; append any extras unchanged.
        ordered = [c for c in _COLUMN_ORDER if c in data.columns]
        ordered += [c for c in data.columns if c not in _COLUMN_ORDER]
        return data[ordered]

    def format_by_district_table(
        data: pd.DataFrame, columns_to_drop: list | None = None
    ):
        column_name_mapping = {
            "Use Header": "Use Category",
            "Use Name": "Zoning Resolution Use Name",
            "NAICS Title": "NAICS Index Use Name",
            "Is Allowed": "Is it Allowed?",
        }
        data_renamed = data.rename(columns=column_name_mapping)
        data_reordered = (
            _order_table_columns(data_renamed)
            .sort_values(
                by=[
                    "Use Group",
                    "Zoning Resolution Use Name",
                    "NAICS Index Use Name",
                ]
            )
            .reset_index(drop=True)
        )
        if columns_to_drop:
            data_reordered = data_reordered.drop(columns=columns_to_drop)
        return format_ui_table(data_reordered)

    def format_by_zr_use_table(data: pd.DataFrame):
        column_name_mapping = {
            "Use Header": "Use Category",
            "Use Name": "Zoning Resolution Use Name",
            "Is Allowed": "Is it Allowed?",
        }
        data_renamed = data.rename(columns=column_name_mapping)
        return format_ui_table(_order_table_columns(data_renamed))

    def format_by_naics_use_table(data: pd.DataFrame):
        column_name_mapping = {
            "Use Header": "Use Category",
            "Use Name": "Zoning Resolution Use Name",
            "NAICS Title": "NAICS Index Use Name",
            "Is Allowed": "Is it Allowed?",
        }
        data_renamed = data.rename(columns=column_name_mapping)
        return format_ui_table(
            _order_table_columns(data_renamed), could_be_empty=True
        )

    return (
        format_by_district_table,
        format_by_naics_use_table,
        format_by_zr_use_table,
    )


@app.cell
def _(
    format_by_district_table,
    format_by_naics_use_table,
    format_by_zr_use_table,
    get_all_uses_by_district,
    get_district_uses_by_naics_index,
    get_district_uses_by_zr_use,
    naics_codes,
    selected_district,
    selected_use_name,
    tab_use_type,
    uses_by_zoning_district_minimal,
):
    _by_district_result = (
        get_all_uses_by_district(
            uses_by_zoning_district_minimal,
            selected_district,
            naics_codes,
            minimal_columns=True,
        )
        if selected_district
        else None
    )
    by_district_result_table = (
        format_by_district_table(_by_district_result)
        if selected_district
        else None
    )
    _by_district_result_zr_only = (
        _by_district_result[
            (_by_district_result["NAICS Title"] == "")
            & (
                ~_by_district_result["Use Name"]
                .astype(str)
                .str.contains("*", regex=False)
            )
        ]
        if selected_district
        else None
    )
    by_district_result_table_zr_only = (
        format_by_district_table(
            _by_district_result_zr_only,
            columns_to_drop=["NAICS Index Use Name"],
        )
        if selected_district
        else None
    )
    tab_by_district_use_filtered_result = mo.ui.tabs(
        {
            "Zoning Resolution terms": by_district_result_table_zr_only,
            "Expanded terms": by_district_result_table,
        }
    )
    result_stack_district = mo.vstack(
        [
            f"You chose '{selected_district}'",
            # by_district_result_table,
            tab_by_district_use_filtered_result,
        ]
    )

    # by use name
    if not selected_use_name:
        by_use_name_result = None
    else:
        if tab_use_type.value == "Zoning Resolution terms":
            by_use_name_result = format_by_zr_use_table(
                get_district_uses_by_zr_use(
                    uses_by_zoning_district_minimal,
                    selected_use_name,
                    minimal_columns=True,
                )
            )
        else:
            # try naics search first, then fall back to ZR use name search if the selected use isn't found in the NAICS index
            try:
                naics_attempt = format_by_naics_use_table(
                    get_district_uses_by_naics_index(
                        uses_by_zoning_district_minimal,
                        naics_codes,
                        selected_use_name,
                        minimal_columns=True,
                        include_all_districts=True,
                    ),
                )
                if isinstance(naics_attempt, str):
                    by_use_name_result = format_by_zr_use_table(
                        get_district_uses_by_zr_use(
                            uses_by_zoning_district_minimal,
                            selected_use_name,
                            minimal_columns=True,
                        )
                    )
                else:
                    by_use_name_result = naics_attempt
            except AssertionError as error:
                by_use_name_result = format_by_zr_use_table(
                    get_district_uses_by_zr_use(
                        uses_by_zoning_district_minimal,
                        selected_use_name,
                        minimal_columns=True,
                    )
                )
    result_stack_use_name = mo.vstack(
        [
            f"You chose '{selected_use_name}'",
            by_use_name_result,
        ]
    )
    return result_stack_district, result_stack_use_name


@app.cell
def _(
    result_stack_district,
    result_stack_use_name,
    selected_district,
    selected_use_name,
):
    conditional_result_district = (
        result_stack_district
        if selected_district
        else "No zoning district selected"
    )

    conditional_result_use_name = (
        result_stack_use_name if selected_use_name else "No use name selected"
    )
    return conditional_result_district, conditional_result_use_name


@app.cell
def _(
    conditional_result_district,
    conditional_result_use_name,
    dropdown_districts,
    query_by_district_intro,
    query_by_district_note,
    query_by_use_intro,
    query_by_use_note,
    tab_use_type,
):
    user_accordion_search = mo.accordion(
        {
            "<strong style='font-size:24px;line-height:24px'>Search by <span style='color:#D76A27'>zoning district</span></strong>  _Find what uses are allowed in a given zoning district_": mo.vstack(
                [
                    mo.md(query_by_district_intro),
                    dropdown_districts,
                    mo.md("---"),
                    conditional_result_district,
                    mo.md("---"),
                    mo.md(query_by_district_note),
                ],
            ),
            "<strong style='font-size:24px;line-height:24px'>Search by <span style='color:#319795'>use</span></strong>  _Find which zoning districts allow which uses_": mo.vstack(
                [
                    mo.md(query_by_use_intro),
                    tab_use_type,
                    mo.md("---"),
                    conditional_result_use_name,
                    mo.md("---"),
                    mo.md(query_by_use_note),
                ]
            ),
        }
    )
    return (user_accordion_search,)


@app.cell
def _(naics_codes, zr_uses):
    user_accordion_view_all = mo.accordion(
        {
            "<span style='font-size:24px;line-height:24px'>View all uses and indexes</span>": mo.vstack(
                [
                    mo.md("### Zoning Resolution Uses"),
                    zr_uses,
                    mo.md("---"),
                    mo.md("### NAICS Indexes"),
                    naics_codes,
                ]
            ),
        }
    )
    return (user_accordion_view_all,)


@app.cell
def _():
    _instructions = mo.md(r"""
    **To look up the zoning district for a lot or area,** use [ZoLa](https://zola.planning.nyc.gov/), the New York City zoning and land use map:

    1. Identify the address of your property of interest.
    2. Search this address on ZoLa to find the lot.
    3. Identify the lot's zoning district in the pop-up window on the right side.
    4. Select that zoning district in the Land Use Lookup tool above to find a list of allowed uses.

    **Some lots may have multiple standard zoning districts.** For example, a lot might be both R6B and C2-4. This indicates a _Commercial District overlay_, where use allowances are governed by the Commercial District.

    **What if a zoning district is not listed on this tool?** Some zoning districts are not listed on this tool, such as SNX, LIC, 125 or DB. These indicate _Special Purpose Districts_ that may have different rules for allowable uses. A full list of Special Purpose Districts can be found in the Zoning Resolution's [Appendix B](https://zr.planning.nyc.gov/appendix-b-index-special-purpose-districts). For more information about rules in these districts, consult [Articles VIII through XIV](https://zr.planning.nyc.gov/article-viii) in the Zoning Resolution._
    """)

    user_accordion_instructions = mo.accordion(
        {
            "<span style='font-size:24px;line-height:24px'>Instructions</span>": mo.vstack(
                [
                    mo.Html(
                        f'<div class="disclaimer">{_instructions.text}</div>'
                    )
                ]
            ),
        }
    )
    return (user_accordion_instructions,)


@app.cell
def _():
    # get data
    return


@app.cell
def _(SOURCE_DATA_DIRECTORY, pl, to_pandas_writable):
    uses_by_zoning_district = to_pandas_writable(
        pl.read_csv(
            str(SOURCE_DATA_DIRECTORY / "uses_by_zoning_district.csv"),
            infer_schema_length=None,
        )
    )
    return (uses_by_zoning_district,)


@app.cell
def _(prepare_results_columns, uses_by_zoning_district):
    uses_by_zoning_district_display = uses_by_zoning_district.copy()
    uses_by_zoning_district_display = uses_by_zoning_district_display[
        [
            "Use Group",
            "Use Header",
            "Use Name",
            "Zoning District",
            "Is Allowed",
            "Is Allowed flag",
            "Special Permit",
            "Size Restrictions",
            "Additional Conditions",
            "Open Use Allowances",
            "Limitations",
            # "Permitted Value",
            # "Use NAICS Code",
            # "NAICS index names to include",
            # "NAICS to subtract",
            # "NAICS index names to subtract",
            # "Processed NAICS",
            # "NAICS Notes",
            # "Not permitted",
            # "Permitted",
            # "Permitted with limitations",
            # "Permitted with limitations*",
            "Use Notes",
        ]
    ]
    zr_uses = prepare_results_columns(uses_by_zoning_district_display)

    uses_by_zoning_district_minimal = uses_by_zoning_district.copy()
    uses_by_zoning_district_minimal = uses_by_zoning_district_minimal[
        [
            "Zoning District",
            "Not permitted",
            "Is Allowed",
            "Special Permit",
            "Size Restrictions",
            "Additional Conditions",
            "Open Use Allowances",
            "Limitations",
            "Use Notes",
            "Use Group",
            "Use Header",
            "Use Name",
            "Use NAICS Code",
            "NAICS index names to include",
            "NAICS to subtract",
            "NAICS index names to subtract",
        ]
    ]
    return uses_by_zoning_district_minimal, zr_uses


@app.cell
def _(SOURCE_DATA_DIRECTORY, pl, to_pandas_writable):
    addressed_naics_titles = to_pandas_writable(
        pl.read_csv(
            str(SOURCE_DATA_DIRECTORY / "addressed_naics_titles.csv"),
            infer_schema_length=None,
        )
    )
    return (addressed_naics_titles,)


@app.cell
def _(SOURCE_DATA_DIRECTORY, pl, to_pandas_writable):
    naics_codes = to_pandas_writable(
        pl.read_csv(
            str(SOURCE_DATA_DIRECTORY / "naics_codes.csv"),
            infer_schema_length=None,
        )
    )
    return (naics_codes,)


@app.cell
def _():
    # utils below are copied from the utils/ files because they can't be packaged and imported with the WASM notebook.
    return


@app.cell
def _(pd):
    def find_permitted_naics_indexes(
        district_uses: pd.DataFrame,
        naics_codes: pd.DataFrame,
    ) -> pd.DataFrame:
        """Return NAICS index rows permitted by a single zoning district's rules.

        This inspects ``district_uses`` for a single ``Zoning District`` and
        builds a set of permitted NAICS index rows (from ``naics_codes``).
        It supports two complementary matching strategies:

        - Code-based matching: values in ``Use NAICS Code`` may be numeric
          prefixes (3-6 digits) or full 6-digit codes; prefixes are matched
          against the appropriate group-code columns in ``naics_codes``.
        - Name-based matching: values in ``NAICS index names to include`` are
          semicolon-delimited NAICS titles and are matched against
          ``naics_codes["NAICS Title"]``.

        Parameters
        ----------
        district_uses : pd.DataFrame
            DataFrame containing zoning district rules. Must contain a single
            unique value in the ``Zoning District`` column.
        naics_codes : pd.DataFrame
            DataFrame containing NAICS index rows and group-code columns.

        Returns
        -------
        pd.DataFrame
            Matched ``naics_codes`` rows with two additional columns appended:
            ``Permitted reason`` (the column used for the match) and
            ``Permitted value`` (the original district value that caused the
            match).
        """

        districts = district_uses["Zoning District"].unique()
        assert len(districts) == 1, (
            f"There should only be one zoning district value, not {districts}"
        )
        permitted_district_uses = district_uses[
            ~district_uses["Not permitted"]
        ]

        # "Use NAICS Code" values are NAICS index codes and are comma-delimited.
        # Reuse the generic `explode_delimited_lists` helper to split, strip,
        # and explode values rather than doing manual string manipulation here.
        permitted_use_codes = (
            explode_delimited_lists(
                permitted_district_uses[["Use NAICS Code"]],
                "Use NAICS Code",
                ",",
            )["Use NAICS Code"]
            .dropna()
            .sort_values()
            .reset_index(drop=True)
            .astype("str")
        )

        # district uses may have no code or a code with 6 to 3 digits
        # Build searches for code-based permitted values in a DRY way.
        # Map: (length of code string, column in `naics_codes`, readable reason)
        length_column_reason = [
            (6, "NAICS Code", "NAICS Code"),
            (5, "Five-digit Group Code", "Five-digit Group Code"),
            (4, "Four-digit Group Code", "Four-digit Group Code"),
            (3, "Three-digit Group Code", "Three-digit Group Code"),
        ]

        code_search_parts = []
        for length, column_name, reason in length_column_reason:
            matches = permitted_use_codes[
                permitted_use_codes.str.len() == length
            ]
            if matches.empty:
                continue
            matches = matches.reset_index(drop=True)
            part = (
                naics_codes[naics_codes[column_name].isin(matches)]
                .sort_values(by=column_name)
                .reset_index(drop=True)
            )
            part["Permitted reason"] = reason
            part["Permitted value"] = part[column_name]
            code_search_parts.append(part)

        code_search = (
            pd.concat(code_search_parts, ignore_index=True)
            if code_search_parts
            else pd.DataFrame(
                columns=naics_codes.columns.to_list()
                + ["Permitted reason", "Permitted value"]
            )
        )

        # Build mapping by exploded Use NAICS Code so we can attach the original
        # permitted district-use columns to each search result before concatenating.
        mapping_codes = permitted_district_uses.copy()
        mapping_codes = explode_delimited_lists(
            mapping_codes, "Use NAICS Code", ",", convert_to_str=True
        )

        code_search = code_search.merge(
            mapping_codes,
            how="left",
            left_on="Permitted value",
            right_on="Use NAICS Code",
        )

        # "NAICS index names to include" values are NAICS index titles and are ; delimited
        if (
            not "NAICS index names to include"
            in permitted_district_uses.columns
        ):
            name_search = pd.DataFrame(
                columns=naics_codes.columns.to_list()
                + ["Permitted reason", "Permitted value"]
            )
        else:
            names_to_include = (
                permitted_district_uses["NAICS index names to include"]
                .dropna()
                .sort_values()
                .reset_index(drop=True)
            )
            # may have a semicolon-delimited list of codes
            split_names_to_include = names_to_include.str.split(";")
            names_to_include = pd.Series(
                [
                    item.strip()
                    for sublist in split_names_to_include
                    for item in sublist
                ]
            )

            name_search = (
                naics_codes[naics_codes["NAICS Title"].isin(names_to_include)]
                .sort_values(by="NAICS Title")
                .reset_index(drop=True)
            )
            name_search["Permitted reason"] = "NAICS Title"
            name_search["Permitted value"] = name_search["NAICS Title"]

            mapping_names = permitted_district_uses.copy()

            mapping_names["NAICS index names to include"] = (
                mapping_names["NAICS index names to include"]
                .dropna()
                .astype(str)
                .str.split(";")
                .apply(
                    lambda lst: (
                        [s.strip() for s in lst]
                        if isinstance(lst, list)
                        else lst
                    )
                )
            )
            mapping_names = mapping_names.explode(
                "NAICS index names to include"
            ).reset_index(drop=True)

            name_search = name_search.merge(
                mapping_names,
                how="left",
                left_on="Permitted value",
                right_on="NAICS index names to include",
            )

        permitted_values = pd.concat(
            [
                code_search,
                name_search,
            ]
        ).reset_index(drop=True)

        return permitted_values

    def explode_delimited_lists(
        df: pd.DataFrame,
        column_to_split: str,
        delimiter: str = ",",
        convert_to_str: bool = False,
        drop_short_numeric_max_len: int | None = None,
    ) -> pd.DataFrame:
        """Split a delimited column into lists, strip whitespace, and explode it.

        The column values are split on the given ``delimiter``, surrounding
        whitespace is stripped from each item, and the column is exploded so each
        row contains a single item.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing the column to split.
        column_to_split : str
            Name of the column to split and explode.
        delimiter : str, optional
            Delimiter to split by, by default ",".
        convert_to_str : bool, optional
            If True, convert the column to string before splitting.
        drop_short_numeric_max_len : int or None, optional
            If provided, drop items which are purely numeric and whose length is
            less than or equal to this value.

        Returns
        -------
        pd.DataFrame
            A new DataFrame where ``column_to_split`` has been expanded and
            exploded into individual rows.
        """

        def _clean_list(lst):
            if not isinstance(lst, list):
                return lst
            if drop_short_numeric_max_len is not None:
                return [
                    s.strip()
                    for s in lst
                    if not (
                        s.strip().isdigit()
                        and len(s.strip()) <= drop_short_numeric_max_len
                    )
                ]
            return [s.strip() for s in lst]

        series = df[column_to_split]
        if convert_to_str:
            series = series.astype(str)
        series = series.str.split(delimiter)
        series = series.apply(
            lambda lst: _clean_list(lst) if isinstance(lst, list) else lst
        )
        df = df.copy()
        df[column_to_split] = series
        return df.explode(column_to_split).reset_index(drop=True)

    def explode_code(code: str) -> list[str]:
        """Expand a NAICS prefix into the list of 6-digit NAICS codes it
        represents.

        Examples
        --------
        - ``"12345"`` -> [``"123450"``, ``"123451"``, ..., ``"123459"``]
        - ``"123"`` -> [``"123000"``, ..., ``"123999"``]

        Parameters
        ----------
        code : str
            Numeric string of length 1..6 representing a NAICS code or prefix.

        Returns
        -------
        list[str]
            List of 6-digit NAICS codes represented by the prefix. If ``code`` is
            already 6 digits this returns a single-item list containing ``code``.

        Raises
        ------
        ValueError
            If ``code`` is not a numeric string or is longer than 6 digits.
        """
        if not isinstance(code, str) or not code.isdigit():
            raise ValueError("Code must be a numeric string")

        code_length = len(code)
        if code_length == 6:
            return [code]
        if code_length < 6:
            # Construct integer range by padding the prefix to the start and end
            # values for the full 6-digit range (e.g. "123" -> 123000..123999).
            start = int(code.ljust(6, "0"))
            end = int(code.ljust(6, "9"))
            return [str(i).zfill(6) for i in range(start, end + 1)]

        raise ValueError("Code must be 6 digits or fewer")

    def exclude_naics_codes(
        permitted_use_codes: pd.DataFrame,
        district_uses: pd.DataFrame,
    ) -> pd.DataFrame:
        """Remove excluded NAICS codes listed in district uses from a set of
        permitted NAICS codes.

        The function looks for ``NAICS to subtract`` entries in ``district_uses``,
        expands any prefixes to full 6-digit codes, and subtracts those codes from
        ``permitted_use_codes``.

        Parameters
        ----------
        permitted_use_codes : pd.DataFrame
            DataFrame of permitted NAICS codes. Must include columns ``NAICS Code``
            and ``Permitted value``.
        district_uses : pd.DataFrame
            DataFrame of district uses containing an optional ``NAICS to subtract``
            column with comma-delimited codes or prefixes.

        Returns
        -------
        pd.DataFrame
            Reduced ``permitted_use_codes`` DataFrame with excluded NAICS codes
            removed.
        """

        permitted_district_uses = district_uses[
            district_uses["Use NAICS Code"].isin(
                permitted_use_codes["Permitted value"]
            )
        ]
        # Split and explode comma-separated lists of codes
        exploded_exclusions = explode_delimited_lists(
            permitted_district_uses, "NAICS to subtract"
        ).dropna(subset=["NAICS to subtract"])
        # Explode 6-or-less-digit codes to lists of 6-digit codes
        exploded_exclusions["NAICS to subtract"] = exploded_exclusions[
            "NAICS to subtract"
        ].apply(explode_code)
        # After expanding each value to a list of 6-digit codes, explode those lists
        # into individual rows so each row contains a single 6-digit code.
        exploded_exclusions = exploded_exclusions.explode(
            "NAICS to subtract"
        ).reset_index(drop=True)

        reduced_use_codes_indicated = permitted_use_codes.merge(
            exploded_exclusions,
            how="left",
            left_on=["NAICS Code", "Permitted value"],
            right_on=["NAICS to subtract", "Use NAICS Code"],
            indicator=True,
            suffixes=(None, "_exclusions"),
        )
        # Filter for 'left_only' rows and drop the indicator column
        reduced_use_codes = reduced_use_codes_indicated[
            reduced_use_codes_indicated["_merge"] == "left_only"
        ][permitted_use_codes.columns.to_list()].reset_index(drop=True)

        return reduced_use_codes

    def exclude_naics_names(
        permitted_use_codes: pd.DataFrame,
        district_uses: pd.DataFrame,
    ) -> pd.DataFrame:
        # Split and explode semicolon-separated lists of names
        exploded_exclusions = explode_delimited_lists(
            district_uses, "NAICS index names to subtract", ";"
        ).dropna(subset=["NAICS index names to subtract"])
        # Split and explode comma-separated lists of codes to join to permitted uses
        exploded_exclusions = explode_delimited_lists(
            exploded_exclusions,
            "Use NAICS Code",
        ).dropna(subset=["Use NAICS Code"])

        reduced_use_names_indicated = permitted_use_codes.merge(
            exploded_exclusions,
            how="left",
            left_on=["NAICS Title", "Permitted value"],
            right_on=["NAICS index names to subtract", "Use NAICS Code"],
            indicator=True,
            suffixes=(None, "_exclusions"),
        )
        # Filter for 'left_only' rows and drop the indicator column
        reduced_use_names = reduced_use_names_indicated[
            reduced_use_names_indicated["_merge"] == "left_only"
        ][permitted_use_codes.columns.to_list()].reset_index(drop=True)

        return reduced_use_names

    return (
        exclude_naics_codes,
        exclude_naics_names,
        find_permitted_naics_indexes,
    )


@app.cell
def _(
    exclude_naics_codes,
    exclude_naics_names,
    find_permitted_naics_indexes,
    pd,
):
    ZR_URL_COLUMNS = [
        "Special Permit",
        "Size Restrictions",
        "Additional Conditions",
        "Open Use Allowances",
        "Limitations",
        "Use Notes",
    ]

    def _reorder_columns(df: pd.DataFrame, first_columns: list):
        # keep the specified columns first (only if they exist), then append any other columns in their current order
        existing_first_cols = [c for c in first_columns if c in df.columns]
        other_cols = [c for c in df.columns if c not in existing_first_cols]
        return df.loc[:, existing_first_cols + other_cols]

    def _clean_falsy_values(df: pd.DataFrame) -> pd.DataFrame:
        # replace all falsy values with an empty string
        df = df.copy()
        for col in df.columns:
            # skip boolean columns to avoid converting False/True to strings
            if pd.api.types.is_bool_dtype(df[col]):
                continue
            df[col] = df[col].replace(False, "")
            df[col] = df[col].replace("False", "")
            df[col] = df[col].fillna("")
        return df

    def prepare_results_columns(
        results: pd.DataFrame,
        first_columns: list | None = None,
        minimal_columns: bool = False,
    ) -> pd.DataFrame:
        cleaned_values = _clean_falsy_values(results)
        if not first_columns:
            return cleaned_values

        primary_columns = first_columns + ZR_URL_COLUMNS
        reordered = _reorder_columns(cleaned_values, primary_columns)
        if minimal_columns:
            return reordered.loc[:, primary_columns]
        return reordered

    def get_district_uses_by_zr_use(
        uses_by_zoning_district: pd.DataFrame,
        use_name: str,
        minimal_columns: bool = False,
    ) -> pd.DataFrame:
        """Return rows from `uses_by_zoning_district` matching a ZR use name.

        Parameters
        ----------
        uses_by_zoning_district : pd.DataFrame
            DataFrame containing zoning resolution uses.
        use_name : str
            The Zoning Resolution `Use Name` to filter for.
        minimal_columns : bool, optional
            When True, the returned DataFrame will contain only the primary
            columns (the listed `first_columns` plus any `ZR_URL_COLUMNS`
            present).

        Returns
        -------
        pd.DataFrame
            A new DataFrame filtered to rows where ``Use Name == use_name``.
        """
        results = uses_by_zoning_district[
            uses_by_zoning_district["Use Name"] == use_name
        ].reset_index(drop=True)
        first_columns = [
            "Zoning District",
            "Is Allowed",
        ]
        return prepare_results_columns(results, first_columns, minimal_columns)

    def get_naics_indexes_by_district(
        uses_by_zoning_district: pd.DataFrame,
        zoning_distrct: str,
        naics_codes: pd.DataFrame,
        minimal_columns: bool = False,
    ) -> pd.DataFrame:
        """Compute permitted NAICS indexes for a single zoning district.

        This composes the lower-level helpers: it finds permitted NAICS
        indexes for the selected district, then applies NAICS-code-based
        exclusions defined in the district uses.

        Parameters
        ----------
        uses_by_zoning_district : pd.DataFrame
            DataFrame with all district uses.
        zoning_distrct : str
            The zoning district string to filter by.
        naics_codes : pd.DataFrame
            DataFrame of NAICS codes and group mappings.
        minimal_columns : bool, optional
            When True, the returned DataFrame will contain only the primary
            columns (the listed `first_columns` plus any `ZR_URL_COLUMNS`
            present).

        Returns
        -------
        pd.DataFrame
            DataFrame of permitted NAICS index rows for the district.
        """
        district_uses = uses_by_zoning_district[
            uses_by_zoning_district["Zoning District"] == zoning_distrct
        ]
        permitted_indexes = find_permitted_naics_indexes(
            district_uses, naics_codes
        )
        if permitted_indexes is None:
            return None

        codes_excluded = exclude_naics_codes(permitted_indexes, district_uses)
        assert "NAICS index names to subtract" in district_uses.columns, (
            "Column 'NAICS index names to subtract' missing from District Uses data"
        )
        results = exclude_naics_names(codes_excluded, district_uses)

        first_columns = [
            "Zoning District",
            "Use Group",
            "Use Header",
            "Use Name",
            "Is Allowed",
            "NAICS Title",
            "NAICS Code",
        ]
        return prepare_results_columns(results, first_columns, minimal_columns)

    def get_all_uses_by_district(
        uses_by_zoning_district: pd.DataFrame,
        zoning_distrct: str,
        naics_codes: pd.DataFrame,
        minimal_columns: bool = False,
    ):
        naics_indexes_by_district = get_naics_indexes_by_district(
            uses_by_zoning_district,
            zoning_distrct,
            naics_codes,
            minimal_columns,
        )

        zr_uses_by_district = uses_by_zoning_district[
            (uses_by_zoning_district["Zoning District"] == zoning_distrct)
            & (uses_by_zoning_district["Use NAICS Code"].isna())
            & ~uses_by_zoning_district["Not permitted"]
        ].copy()
        if not zr_uses_by_district.empty:
            zr_uses_by_district.loc[:, "NAICS Title"] = ""
            zr_uses_by_district.loc[:, "NAICS Code"] = ""
            zr_uses_by_district.loc[:, "Permitted reason"] = "ZR use name"
            zr_uses_by_district.loc[:, "Permitted value"] = (
                zr_uses_by_district["Use Name"]
            )
            first_columns = [
                "Zoning District",
                "Use Group",
                "Use Header",
                "Use Name",
                "Is Allowed",
                "NAICS Title",
                "NAICS Code",
            ]
            zr_uses_by_district = prepare_results_columns(
                zr_uses_by_district, first_columns, minimal_columns
            )

        results = pd.concat(
            [zr_uses_by_district, naics_indexes_by_district]
        ).reset_index(drop=True)
        return results

    def get_district_uses_by_naics_index(
        uses_by_zoning_district: pd.DataFrame,
        naics_codes: pd.DataFrame,
        naics_title: str,
        minimal_columns: bool = False,
        include_all_districts: bool = False,
    ) -> pd.DataFrame:
        """Return zoning-district-level permitted uses for a given NAICS title.

        For each zoning district, compute permitted NAICS indexes and collect
        the results into a single DataFrame. The returned DataFrame is ordered
        to put commonly-used columns first when present.

        Parameters
        ----------
        uses_by_zoning_district : pd.DataFrame
            DataFrame with district uses.
        naics_codes : pd.DataFrame
            DataFrame of NAICS code rows (should include the selected NAICS title row).
        naics_title : str
            The NAICS index title to search for.
        minimal_columns : bool, optional
            When True, the returned DataFrame will contain only the primary
            columns (the listed `first_columns` plus any `ZR_URL_COLUMNS`
            present).

        Returns
        -------
        pd.DataFrame
            DataFrame of permitted NAICS entries across zoning districts for the
            provided NAICS title.
        """
        naics_codes_single = naics_codes[
            naics_codes["NAICS Title"] == naics_title
        ]
        assert len(naics_codes_single) == 1, (
            f"There should only be one NAICS index, not {len(naics_codes_single)}"
        )
        districts_results = []
        districts = (
            uses_by_zoning_district["Zoning District"].unique().tolist()
        )
        for district in districts:
            district_result = get_naics_indexes_by_district(
                uses_by_zoning_district, district, naics_codes_single
            )
            district_result["Zoning District"] = district
            districts_results.append(district_result)

        results = pd.concat(districts_results, ignore_index=True)
        if results.empty:
            return pd.DataFrame()

        assert len(results["Use Name"].unique().tolist()) == 1
        if include_all_districts:
            all_use_districts = uses_by_zoning_district[
                uses_by_zoning_district["Use Name"]
                == results["Use Name"].iloc[0]
            ]
            all_use_districts = all_use_districts[
                [
                    "Use Group",
                    "Use Header",
                    "Use Name",
                    "Zoning District",
                    "Is Allowed",
                ]
            ]
            all_use_districts["NAICS Title"] = naics_title
            all_use_districts["NAICS Code"] = naics_codes_single[
                "NAICS Code"
            ].iloc[0]
            results = all_use_districts.merge(
                results,
                how="left",
                on=[
                    "NAICS Title",
                    "NAICS Code",
                    "Use Group",
                    "Use Header",
                    "Use Name",
                    "Zoning District",
                    "Is Allowed",
                ],
            )

        first_columns = [
            "Zoning District",
            "Is Allowed",
            "NAICS Title",
            "NAICS Code",
            "Use Group",
            "Use Header",
            "Use Name",
        ]
        return prepare_results_columns(results, first_columns, minimal_columns)

    return (
        get_all_uses_by_district,
        get_district_uses_by_naics_index,
        get_district_uses_by_zr_use,
        prepare_results_columns,
    )


if __name__ == "__main__":
    app.run()

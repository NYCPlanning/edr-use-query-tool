import marimo

__generated_with = "0.15.3"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import pandas as pd
    import polars as pl

    # Using mo.notebook_location() to access data both locally and when running via WebAssembly (e.g. hosted on GitHub Pages)
    SOURCE_DATA_DIRECTORY = mo.notebook_location() / "output" / "for_query_tool"


@app.cell(hide_code=True)
def _():
    mo.md(r"""# THIS IS AN EXPERIMENTAL TEST APPLICATION""")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    # Use Query Tool

    This tool helps users identify permitted uses for parcels of land in New York City. It is based on the NYC Department of City Planning's [Zoning Resolution](https://zoningresolution.planning.nyc.gov/) and the [North American Industry Classification System](https://www.census.gov/naics/?99967) (NAICS).

    It can can be used to either:

    1. **Query by zoning district** to find which types of business are allowed in a certain zoning district
    2. **Query by NAICS industry** to find which zoning districts allow a certain industry type
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""---""")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""This tool uses two tables:""")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ### Uses by Zoning District

    - one row per use and zoning distrcit
    - columns related to the use and the allowance details for the zoning district
    """
    )
    return


@app.cell
def _():
    uses_by_zoning_district_polars = pl.read_csv(
        str(SOURCE_DATA_DIRECTORY / "uses_by_zoning_district.csv"),
        infer_schema_length=None,
    )
    # Pandas fails to read csvs from URLs with error "BadGzipFile: Not a gzipped file (b'sp')"
    uses_by_zoning_district = uses_by_zoning_district_polars.to_pandas()
    uses_by_zoning_district
    return (uses_by_zoning_district,)


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ### NAICS Codes

    - one row per 6-digit industry code
    - columns related the code and it's industry groups
    """
    )
    return


@app.cell
def _():
    naics_codes_polars = pl.read_csv(
        str(SOURCE_DATA_DIRECTORY / "naics_codes.csv"),
        infer_schema_length=None,
    )
    naics_codes = naics_codes_polars.to_pandas()
    naics_codes
    return (naics_codes,)


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    **DISCLAIMERS**

    - Not all uses in the Zoning Resolution with designated NAICS code have been parsed for use in this tool yet.
    - Some uses in the Zoning Resolution do not have designated NAICS codes and cannot be easily queried by this tool. For such uses, use the Search feature in the two tables above and manually compare the relevant NAICS title(s) to the use name(s).
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""----""")
    return


@app.cell(hide_code=True)
def section_query_by_district():
    mo.md(r"""## Query uses by zoning district""")
    return


@app.cell
def _(uses_by_zoning_district):
    # dropdown to select district
    dropdown_district = mo.ui.dropdown.from_series(
        uses_by_zoning_district["Zoning District"],
        label="Select a Zoning District: ",
        searchable=True,
    )
    dropdown_district
    return (dropdown_district,)


@app.cell
def _(dropdown_district, uses_by_zoning_district):
    district_uses_focus = uses_by_zoning_district[
        uses_by_zoning_district["Zoning District"] == dropdown_district.value
    ].reset_index(drop=True)
    district_uses_focus
    return (district_uses_focus,)


@app.function
def find_permitted_naics_codes(
    district_uses: pd.DataFrame,
    naics_codes: pd.DataFrame,
) -> pd.DataFrame:
    permitted_district_uses = district_uses[~district_uses["Not permitted"]]
    permitted_use_codes = (
        permitted_district_uses["Use NAICS Code"]
        .dropna()
        .sort_values()
        .reset_index(drop=True)
    )
    # district uses may have a comma-separated list of codes
    split_values = permitted_use_codes.str.split(",")
    permitted_use_codes = pd.Series(
        [item for sublist in split_values for item in sublist]
    )
    # TODO handle the NAICS to subtract values

    # district uses may have no code or a code with 6 to 3 digits
    use_codes_six_digits = permitted_use_codes[
        permitted_use_codes.str.len() == 6
    ].reset_index(drop=True)
    use_codes_five_digits = permitted_use_codes[
        permitted_use_codes.str.len() == 5
    ].reset_index(drop=True)
    use_codes_four_digits = permitted_use_codes[
        permitted_use_codes.str.len() == 4
    ].reset_index(drop=True)
    use_codes_three_digits = permitted_use_codes[
        permitted_use_codes.str.len() == 3
    ].reset_index(drop=True)

    six_digit_search = (
        naics_codes[naics_codes["NAICS Code"].isin(use_codes_six_digits)]
        .sort_values(by="NAICS Code")
        .reset_index(drop=True)
    )
    six_digit_search["Permitted reason"] = "NAICS Code"
    six_digit_search["Permitted value"] = six_digit_search["NAICS Code"]
    five_digit_search = (
        naics_codes[
            naics_codes["Five-digit Group Code"].isin(use_codes_five_digits)
        ]
        .sort_values(by="Five-digit Group Code")
        .reset_index(drop=True)
    )
    five_digit_search["Permitted reason"] = "Five-digit Group Code"
    five_digit_search["Permitted value"] = five_digit_search[
        "Five-digit Group Code"
    ]
    four_digit_search = (
        naics_codes[
            naics_codes["Four-digit Group Code"].isin(use_codes_four_digits)
        ]
        .sort_values(by="Four-digit Group Code")
        .reset_index(drop=True)
    )
    four_digit_search["Permitted reason"] = "Four-digit Group Code"
    four_digit_search["Permitted value"] = four_digit_search[
        "Four-digit Group Code"
    ]
    three_digit_search = (
        naics_codes[
            naics_codes["Three-digit Group Code"].isin(use_codes_three_digits)
        ]
        .sort_values(by="Three-digit Group Code")
        .reset_index(drop=True)
    )
    three_digit_search["Permitted reason"] = "Three-digit Group Code"
    three_digit_search["Permitted value"] = three_digit_search[
        "Three-digit Group Code"
    ]

    return pd.concat(
        [
            six_digit_search,
            five_digit_search,
            four_digit_search,
            three_digit_search,
        ]
    ).reset_index(drop=True)


@app.cell(hide_code=True)
def _():
    mo.md(r"""### Permitted uses""")
    return


@app.cell
def _(district_uses_focus, naics_codes):
    permitted_use_codes = find_permitted_naics_codes(
        district_uses_focus, naics_codes
    )
    permitted_use_codes
    return (permitted_use_codes,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""### Focus on a single permitted use""")
    return


@app.cell
def _(permitted_use_codes):
    dropdown_permitted_naics_title = mo.ui.dropdown.from_series(
        permitted_use_codes["NAICS Title"],
        label="Select a NAICS Title: ",
        searchable=True,
    )
    dropdown_permitted_naics_title
    return (dropdown_permitted_naics_title,)


@app.cell
def _(dropdown_permitted_naics_title, permitted_use_codes):
    permitted_use_codes_focus = permitted_use_codes[
        permitted_use_codes["NAICS Title"] == dropdown_permitted_naics_title.value
    ].reset_index(drop=True)
    permitted_use_codes_focus
    return (permitted_use_codes_focus,)


@app.cell
def _(district_uses_focus, permitted_use_codes_focus):
    district_uses_focus.merge(
        permitted_use_codes_focus["Permitted value"],
        how="inner",
        left_on="Use NAICS Code",
        right_on="Permitted value",
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""----""")
    return


@app.cell(hide_code=True)
def section_query_by_naics():
    mo.md(r"""## Query zoning districts by use""")
    return


@app.cell
def _(naics_codes):
    # dropdown to select district
    # TODO add toggle to select code or title
    dropdown_naics_title = mo.ui.dropdown.from_series(
        naics_codes["NAICS Title"],
        label="Select a NAICS title: ",
        searchable=True,
    )
    dropdown_naics_title
    return (dropdown_naics_title,)


@app.cell
def _():
    # TODO consider option to select strictness of code matching by digit (in initial selection so user can see all codes in an industry group)
    return


@app.cell
def _(dropdown_naics_title, naics_codes):
    naics_code_details_focus = naics_codes[
        naics_codes["NAICS Title"] == dropdown_naics_title.value
    ].reset_index(drop=True)
    naics_code_details_focus
    return (naics_code_details_focus,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""### Permitted zoning districts""")
    return


@app.cell
def _(naics_code_details_focus):
    def find_permitted_districts(
        naics_codes: pd.DataFrame, district_uses: pd.DataFrame
    ) -> pd.DataFrame:
        permitted_district_uses = district_uses[~district_uses["Not permitted"]]
        six_digit_search_focus = permitted_district_uses.merge(
            naics_code_details_focus,
            how="inner",
            left_on="Use NAICS Code",
            right_on="NAICS Code",
        )
        if not six_digit_search_focus.empty:
            return six_digit_search_focus

        five_digit_search_focus = permitted_district_uses.merge(
            naics_code_details_focus,
            how="inner",
            left_on="Use NAICS Code",
            right_on="Five-digit Group Code",
        )
        if not five_digit_search_focus.empty:
            return five_digit_search_focus

        four_digit_search_focus = permitted_district_uses.merge(
            naics_code_details_focus,
            how="inner",
            left_on="Use NAICS Code",
            right_on="Four-digit Group Code",
        )
        if not four_digit_search_focus.empty:
            return four_digit_search_focus

        three_digit_search_focus = permitted_district_uses.merge(
            naics_code_details_focus,
            how="inner",
            left_on="Use NAICS Code",
            right_on="Three-digit Group Code",
        )
        if not three_digit_search_focus.empty:
            return three_digit_search_focus

        return pd.DataFrame()
    return (find_permitted_districts,)


@app.cell
def _(
    find_permitted_districts,
    naics_code_details_focus,
    uses_by_zoning_district,
):
    permitted_districts_focus = find_permitted_districts(
        naics_code_details_focus, uses_by_zoning_district
    )
    permitted_districts_focus
    return


if __name__ == "__main__":
    app.run()

import marimo

__generated_with = "0.15.3"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Process Use Group data""")
    return


@app.cell
def _():
    import marimo as mo
    from pathlib import Path
    import numpy as np
    import pandas as pd
    import re
    return Path, mo, np, pd, re


@app.cell
def _(Path):
    RESOURCES_DIRECTORY = Path("./resources")
    OUTPUT_DIRECTORY = Path("./output")
    return OUTPUT_DIRECTORY, RESOURCES_DIRECTORY


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Load use groups""")
    return


@app.cell
def _(RESOURCES_DIRECTORY, pd):
    use_groups_raw = pd.read_excel(
        RESOURCES_DIRECTORY / "Use Group Chart - Transposed All UGs.xlsx"
    )
    use_groups_raw
    return (use_groups_raw,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Clean use groups""")
    return


@app.cell
def _(pd):
    def clean_use_groups(raw_use_groups: pd.DataFrame) -> pd.DataFrame:
        naics_description_columns = ["Uses Header", "Uses (NAICS Code)"]
        other_columns = [
            col
            for col in raw_use_groups.columns
            if col not in naics_description_columns
        ]
        cleaned = raw_use_groups.replace(
            {r"\s+$": "", r"^\s+": ""}, regex=True
        ).replace(r"\n", "", regex=True)
        # cleaned[other_columns] = cleaned[other_columns].replace(" ", "")

        return cleaned
    return (clean_use_groups,)


@app.cell
def _(clean_use_groups, use_groups_raw):
    use_groups_cleaned = clean_use_groups(use_groups_raw)
    use_groups_cleaned
    return (use_groups_cleaned,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Parse zoning district values""")
    return


@app.cell
def _():
    id_columns = [
        "Use Group",
        "Use Header",
        "Use Name",
        "Use Name Full",
        "Use NAICS Code",
        "NAICS Notes",
        "NAICS to subtract",
    ]
    columns_to_ignore = [
        "PRC",
        "NAICS_Type",
    ]
    return columns_to_ignore, id_columns


@app.cell
def _(columns_to_ignore, id_columns, use_groups_cleaned):
    use_groups_zoning_districts = use_groups_cleaned.drop(
        columns=columns_to_ignore
    ).melt(
        id_vars=id_columns,
        var_name="Zoning District",
        value_name="Permitted Value",
    )

    use_groups_zoning_districts
    return (use_groups_zoning_districts,)


@app.cell
def _(OUTPUT_DIRECTORY, use_groups_zoning_districts):
    use_groups_zoning_districts.to_csv(
        OUTPUT_DIRECTORY / "use_groups_zoning_districts_full.csv", index=False
    )
    return


@app.cell
def _(use_groups_zoning_districts):
    use_groups_zoning_districts["Permitted Value"].value_counts()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Parse permitted values""")
    return


@app.cell
def _():
    PERMITTED_CHARACTERS = {
        "–": "Not permitted",
        "●": "Permitted",
        "♦": "Permitted with limitations",
        "*": "Permitted with limitations*",
        "○": "Special permit required",
        "S": "Size restriction",
        "P": "Additional conditions",
        "U": "Open use allowances",
    }
    PERMITTED_VALUE_COLUMNS = list(PERMITTED_CHARACTERS.values())
    return (PERMITTED_CHARACTERS,)


@app.cell
def _(PERMITTED_CHARACTERS, pd):
    def parse_permitted_value(row: pd.Series) -> list:
        for character in PERMITTED_CHARACTERS.keys():
            if character in row["Permitted Value"]:
                row[PERMITTED_CHARACTERS[character]] = True
            else:
                row[PERMITTED_CHARACTERS[character]] = False
        return row
    return (parse_permitted_value,)


@app.cell
def _(parse_permitted_value, use_groups_zoning_districts):
    use_groups_district_allowances = use_groups_zoning_districts.apply(
        parse_permitted_value, axis=1
    )
    use_groups_district_allowances
    return (use_groups_district_allowances,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Create "Is Allowed" column""")
    return


@app.cell
def _(use_groups_district_allowances):
    use_groups_district_allowances["Is Allowed"] = use_groups_district_allowances[
        "Not permitted"
    ].apply(lambda row: "No" if row else "Yes")
    return


@app.cell
def _(use_groups_district_allowances):
    use_groups_district_allowances["Is Allowed"] = use_groups_district_allowances[
        "Is Allowed"
    ] + use_groups_district_allowances["Special permit required"].apply(
        lambda x: ", by special permit" if x else ""
    )
    use_groups_district_allowances["Is Allowed"] = use_groups_district_allowances[
        "Is Allowed"
    ] + use_groups_district_allowances["Size restriction"].apply(
        lambda x: ", subject to size restrictions" if x else ""
    )
    use_groups_district_allowances["Is Allowed"] = use_groups_district_allowances[
        "Is Allowed"
    ] + use_groups_district_allowances["Additional conditions"].apply(
        lambda x: ", subject to additional conditions" if x else ""
    )
    use_groups_district_allowances["Is Allowed"] = use_groups_district_allowances[
        "Is Allowed"
    ] + use_groups_district_allowances["Open use allowances"].apply(
        lambda x: ", subject to open use allowances" if x else ""
    )
    use_groups_district_allowances["Is Allowed"] = use_groups_district_allowances[
        "Is Allowed"
    ] + use_groups_district_allowances["Permitted with limitations"].apply(
        lambda x: ", with limited applicability" if x else ""
    )
    use_groups_district_allowances["Is Allowed"] = use_groups_district_allowances[
        "Is Allowed"
    ] + use_groups_district_allowances["Permitted with limitations*"].apply(
        lambda x: ", with limited applicability" if x else ""
    )
    return


@app.cell
def _(use_groups_district_allowances):
    use_groups_district_allowances
    return


@app.cell
def _(use_groups_district_allowances):
    use_groups_district_allowances["Is Allowed"].value_counts()
    return


@app.cell
def _(OUTPUT_DIRECTORY, use_groups_district_allowances):
    use_groups_district_allowances.to_csv(
        OUTPUT_DIRECTORY / "use_groups_district_allowances.csv", index=False
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Parse Use NAICS Code values""")
    return


@app.cell
def _(use_groups_district_allowances):
    use_groups_naics_codes = use_groups_district_allowances.copy()
    return (use_groups_naics_codes,)


@app.cell
def _(use_groups_naics_codes):
    use_groups_naics_codes["Use NAICS Code"].value_counts()
    return


@app.function
def parse_naics_text(naics_text: str | float) -> str:
    if isinstance(naics_text, float):
        return naics_text
    naics_text = naics_text.replace("in", "")
    naics_text = naics_text.replace(", and ", ", ")
    naics_text = naics_text.replace(" and ", ", ")
    return str(naics_text.strip())


@app.cell
def _(use_groups_naics_codes):
    use_groups_naics_codes["Use NAICS Code"] = use_groups_naics_codes[
        "Use NAICS Code"
    ].apply(parse_naics_text)
    use_groups_naics_codes["Use NAICS Code"].value_counts()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Add ZR links

    For additional conditions, size limitations, etc.
    """
    )
    return


@app.cell
def _():
    residential_dist_reg_links = {
        "UGI - gen": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-111",
        "UGI - addl cond": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-112",
        "UGI - special perm": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-113",
        "UGI - addl park": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-114",
        "UGII - gen": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-121",
        "UGII - addl cond": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-122",
        "UGIII - gen": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-131",
        "UGIII - size": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-132",
        "UGIII - addl cond": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-133",
        "UGIII - special perm": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-134",
        "UGIII - addl park": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-135",
        "UGIV - gen": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-141",
        "UGIV - size": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-142",
        "UGIV - addl cond": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-143",
        "UGIV - special perm": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-144",
        "UGV - ALL": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-15",
        "UGVII - ALL": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-17",
        "UGVIII - ALL": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-18",
        "Adult Establishments": "https://zr.planning.nyc.gov/article-ii/chapter-2#22-01",
    }
    return (residential_dist_reg_links,)


@app.cell
def _():
    commercial_dist_reg_links = {
        "UGI - gen": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-111",
        "UGI - size": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-112",
        "UGI - addl cond": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-113",
        "UGI - open use": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-114",
        "UGI - special perm": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-115",
        "UGI - addl park": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-116",
        "UGII - gen": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-121",
        "UGII - limited appl": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-122",
        "UGII - addl cond": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-123",
        "UGIII - gen": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-131",
        "UGIII - size": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-132",
        "UGIII - addl cond": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-133",
        "UGIII - special perm": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-134",
        "UGIII - addl park": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-135",
        "UGIV - gen": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-141",
        "UGIV - size": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-142",
        "UGIV - addl cond": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-143",
        "UGIV - open use": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-144",
        "UGIV - special perm": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-145",
        "UGV - gen": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-151",
        "UGV - limited appl": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-152",
        "UGV - addl cond": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-153",
        "UGV - open use": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-154",
        "UGV - special perm": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-155",
        "UGV - addl park": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-156",
        "UGVI - gen": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-161",
        "UGVI - size": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-162",
        "UGVI - addl cond": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-163",
        "UGVI - open use": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-164",
        "UGVI - special perm": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-165",
        "UGVI - addl park": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-166",
        "UGVII - gen": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-171",
        "UGVII - limited appl": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-172",
        "UGVII - addl cond": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-173",
        "UGVIII - gen": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-181",
        "UGVIII - size": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-182",
        "UGVIII - addl cond": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-183",
        "UGVIII - open use": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-184",
        "UGVIII - special perm": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-185",
        "UGVIII - addl park": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-186",
        "UGIX - gen": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-191",
        "UGIX - limited appl": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-192",
        "UGIX - size": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-193",
        "UGIX - addl cond": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-194",
        "UGIX - open use": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-195",
        "UGIX - special perm": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-196",
        "UGIX - addl park": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-197",
        "UGX - gen": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-201",
        "UGX - size": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-202",
        "UGX - addl cond": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-203",
        "UGX - addl park": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-204",
        "Adult Establishments": "https://zr.planning.nyc.gov/article-iii/chapter-2#32-01",
    }
    return (commercial_dist_reg_links,)


@app.cell
def _():
    manufacturing_dist_reg_links = {
        "UGI - gen": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-111",
        "UGI - addl cond": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-112",
        "UGI - open use": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-113",
        "UGI - special perm": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-114",
        "UGI - addl park": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-115",
        "UGII - ALL": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-12",
        "UGIII - gen": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-131",
        "UGIII - addl cond": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-132",
        "UGIII - special perm": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-133",
        "UGIII - addl park": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-134",
        "UGIV - gen": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-141",
        "UGIV - size": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-142",
        "UGIV - addl cond": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-143",
        "UGIV - open use": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-144",
        "UGIV - special perm": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-145",
        "UGV - gen": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-151",
        "UGV - addl cond": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-152",
        "UGV - open use": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-153",
        "UGV - addl park": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-154",
        "UGVI - gen": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-161",
        "UGVI - size": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-162",
        "UGVI - addl cond": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-163",
        "UGVI - open use": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-164",
        "UGVI - addl park": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-165",
        "UGVII - ALL": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-17",
        "UGVIII - gen": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-181",
        "UGVIII - size": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-182",
        "UGVIII - addl cond": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-183",
        "UGVIII - open use": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-184",
        "UGVIII - special perm": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-185",
        "UGVIII - addl park": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-186",
        "UGIX - gen": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-191",
        "UGIX - limited appl": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-192",
        "UGIX - addl cond": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-193",
        "UGIX - open use": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-194",
        "UGX - gen": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-201",
        "UGX - addl cond": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-202",
        "Adult Establishments": "https://zr.planning.nyc.gov/article-iv/chapter-2#42-01",
    }
    return (manufacturing_dist_reg_links,)


@app.cell
def _(
    commercial_dist_reg_links,
    manufacturing_dist_reg_links,
    pd,
    re,
    residential_dist_reg_links,
):
    def add_zr_links(df_input: pd.DataFrame) -> pd.DataFrame:
        df_output = df_input.copy()
        numerals = r"\b[IVX]+\b"
        for index, row in df_output.iterrows():
            if row["Zoning District"][:1] == "R":
                if row["Permitted with limitations"] == True:
                    try:
                        df_output.loc[index, "Permitted with limitations"] = (
                            residential_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - limited appl"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Permitted with limitations"] = (
                            residential_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Permitted with limitations"] == False:
                    df_output.loc[index, "Permitted with limitations"] = ""

                if row["Permitted with limitations*"] == False:
                    df_output.loc[index, "Permitted with limitations*"] = ""

                if row["Special permit required"] == True:
                    try:
                        df_output.loc[index, "Special permit required"] = (
                            residential_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - special perm"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Special permit required"] = (
                            residential_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Special permit required"] == False:
                    df_output.loc[index, "Special permit required"] = ""

                if row["Size restriction"] == True:
                    try:
                        df_output.loc[index, "Size restriction"] = (
                            residential_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - size"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Size restriction"] = (
                            residential_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Size restriction"] == False:
                    df_output.loc[index, "Size restriction"] = ""

                if row["Additional conditions"] == True:
                    try:
                        df_output.loc[index, "Additional conditions"] = (
                            residential_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - addl cond"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Additional conditions"] = (
                            residential_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Additional conditions"] == False:
                    df_output.loc[index, "Additional conditions"] = ""

                if row["Open use allowances"] == True:
                    try:
                        df_output.loc[index, "Open use allowances"] = (
                            residential_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - open use"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Open use allowances"] = (
                            residential_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Open use allowances"] == False:
                    df_output.loc[index, "Open use allowances"] = ""

            elif row["Zoning District"][:1] == "C":
                if row["Permitted with limitations"] == True:
                    try:
                        df_output.loc[index, "Permitted with limitations"] = (
                            commercial_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - limited appl"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Permitted with limitations"] = (
                            commercial_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Permitted with limitations"] == False:
                    df_output.loc[index, "Permitted with limitations"] = ""

                if row["Permitted with limitations*"] == False:
                    df_output.loc[index, "Permitted with limitations*"] = ""

                if row["Special permit required"] == True:
                    try:
                        df_output.loc[index, "Special permit required"] = (
                            commercial_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - special perm"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Special permit required"] = (
                            commercial_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Special permit required"] == False:
                    df_output.loc[index, "Special permit required"] = ""

                if row["Size restriction"] == True:
                    try:
                        df_output.loc[index, "Size restriction"] = (
                            commercial_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - size"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Size restriction"] = (
                            commercial_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Size restriction"] == False:
                    df_output.loc[index, "Size restriction"] = ""

                if row["Additional conditions"] == True:
                    try:
                        df_output.loc[index, "Additional conditions"] = (
                            commercial_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - addl cond"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Additional conditions"] = (
                            commercial_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Additional conditions"] == False:
                    df_output.loc[index, "Additional conditions"] = ""

                if row["Open use allowances"] == True:
                    try:
                        df_output.loc[index, "Open use allowances"] = (
                            commercial_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - open use"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Open use allowances"] = (
                            commercial_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Open use allowances"] == False:
                    df_output.loc[index, "Open use allowances"] = ""

            elif row["Zoning District"][:1] == "M":
                if row["Permitted with limitations"] == True:
                    try:
                        df_output.loc[index, "Permitted with limitations"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - limited appl"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Permitted with limitations"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Permitted with limitations"] == False:
                    df_output.loc[index, "Permitted with limitations"] = ""

                if row["Permitted with limitations*"] == True:
                    try:
                        df_output.loc[index, "Permitted with limitations*"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - limited appl"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Permitted with limitations*"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Permitted with limitations*"] == False:
                    df_output.loc[index, "Permitted with limitations*"] = ""

                if row["Special permit required"] == True:
                    try:
                        df_output.loc[index, "Special permit required"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - special perm"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Special permit required"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Special permit required"] == False:
                    df_output.loc[index, "Special permit required"] = ""

                if row["Size restriction"] == True:
                    try:
                        df_output.loc[index, "Size restriction"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - size"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Size restriction"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Size restriction"] == False:
                    df_output.loc[index, "Size restriction"] = ""

                if row["Additional conditions"] == True:
                    try:
                        df_output.loc[index, "Additional conditions"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - addl cond"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Additional conditions"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Additional conditions"] == False:
                    df_output.loc[index, "Additional conditions"] = ""

                if row["Open use allowances"] == True:
                    try:
                        df_output.loc[index, "Open use allowances"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - open use"
                            ]
                        )
                    except KeyError:
                        df_output.loc[index, "Open use allowances"] = (
                            manufacturing_dist_reg_links[
                                f"UG{re.findall(numerals, row['Use Group'])[0]} - ALL"
                            ]
                        )
                elif row["Open use allowances"] == False:
                    df_output.loc[index, "Open use allowances"] = ""

        return df_output
    return (add_zr_links,)


@app.cell
def _(add_zr_links, use_groups_naics_codes):
    use_groups_zr_links = add_zr_links(use_groups_naics_codes)
    use_groups_zr_links
    return (use_groups_zr_links,)


@app.cell
def _(use_groups_zr_links):
    use_groups_zr_links["Limitations"] = (
        use_groups_zr_links["Permitted with limitations"]
        + use_groups_zr_links["Permitted with limitations*"]
    )
    use_groups_zr_links
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Export processed Use Group data""")
    return


@app.cell
def _(use_groups_zr_links):
    use_groups_output = use_groups_zr_links.rename(
        columns={
            "Special permit required": "Special Permit",
            "Size restriction": "Size Restrictions",
            "Additional conditions": "Additional Conditions",
            "Open use allowances": "Open Use Allowances",
        }
    )
    use_groups_output
    return (use_groups_output,)


@app.cell
def _(use_groups_output):
    # Future add for ZR Link text - add specific article/section
    use_groups_output_excel = use_groups_output[
        [
            "Use Group",
            "Use Header",
            "Use Name",
            "Zoning District",
            "Is Allowed",
            "Limitations",
            "Special Permit",
            "Size Restrictions",
            "Additional Conditions",
            "Open Use Allowances",
        ]
    ]
    use_groups_output_excel["Limitations"] = use_groups_output_excel[
        "Limitations"
    ].apply(lambda x: f'=HYPERLINK("{x}", "ZR Link")' if x else "")
    use_groups_output_excel["Special Permit"] = use_groups_output_excel[
        "Special Permit"
    ].apply(lambda x: f'=HYPERLINK("{x}", "ZR Link")' if x else "")
    use_groups_output_excel["Size Restrictions"] = use_groups_output_excel[
        "Size Restrictions"
    ].apply(lambda x: f'=HYPERLINK("{x}", "ZR Link")' if x else "")
    use_groups_output_excel["Additional Conditions"] = use_groups_output_excel[
        "Additional Conditions"
    ].apply(lambda x: f'=HYPERLINK("{x}", "ZR Link")' if x else "")
    use_groups_output_excel["Open Use Allowances"] = use_groups_output_excel[
        "Open Use Allowances"
    ].apply(lambda x: f'=HYPERLINK("{x}", "ZR Link")' if x else "")
    use_groups_output_excel
    return (use_groups_output_excel,)


@app.cell
def _(OUTPUT_DIRECTORY, use_groups_output):
    use_groups_output.to_csv(
        OUTPUT_DIRECTORY / "usegroups_by_zoningdist_with_ZR_links.csv",
        index=False,
    )
    use_groups_output.to_csv(
        OUTPUT_DIRECTORY / "for_query_tool" / "uses_by_zoning_district.csv",
        index=False,
    )
    return


@app.cell
def _(OUTPUT_DIRECTORY, use_groups_output_excel):
    use_groups_output_excel.to_excel(
        OUTPUT_DIRECTORY / "usegroups_by_zoningdist_with_ZR_links.xlsx",
        index=False,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Proces NAICS codes""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Load NAICS codes""")
    return


@app.cell
def _(RESOURCES_DIRECTORY, pd):
    code_groups_raw = pd.read_csv(RESOURCES_DIRECTORY / "naics_codes.csv")
    code_groups_raw
    return (code_groups_raw,)


@app.cell
def _(RESOURCES_DIRECTORY, pd):
    naics_codes_new_raw = pd.read_excel(
        RESOURCES_DIRECTORY / "2022_NAICS_Index_File.xlsx", dtype=str
    )
    naics_codes_new_raw
    return (naics_codes_new_raw,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Clean NAICS codes""")
    return


@app.cell
def _(code_groups_raw):
    code_groups_cleaned = code_groups_raw.rename(
        columns={"2022 NAICS US   Code": "2022 NAICS US Code"}
    ).drop(columns=["Seq. No."])
    code_groups_cleaned["2022 NAICS US Title"] = code_groups_cleaned[
        "2022 NAICS US Title"
    ].map(lambda x: x.strip())
    code_groups_cleaned
    return (code_groups_cleaned,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Create digit code columns (or "Join industry groups to 6-digit codes"?)""")
    return


@app.cell
def _(np):
    def get_code_group_digits(code: str, digit_number: int) -> str:
        if len(code) < digit_number:
            return np.nan
        return code[:digit_number]
    return (get_code_group_digits,)


@app.cell
def _(naics_codes_new_raw):
    six_digit_codes = naics_codes_new_raw.copy()
    return (six_digit_codes,)


@app.cell
def _(code_groups_cleaned):
    code_groups_cleaned["code original"] = code_groups_cleaned[
        "2022 NAICS US Code"
    ]
    code_groups_cleaned["code original"].value_counts()
    return


@app.cell
def _(code_groups_cleaned, get_code_group_digits):
    code_groups_cleaned["code_group_one"] = code_groups_cleaned[
        "code original"
    ].apply(get_code_group_digits, digit_number=1)
    code_groups_cleaned["code_group_two"] = code_groups_cleaned[
        "code original"
    ].apply(get_code_group_digits, digit_number=2)
    code_groups_cleaned["code_group_three"] = code_groups_cleaned[
        "code original"
    ].apply(get_code_group_digits, digit_number=3)
    code_groups_cleaned["code_group_four"] = code_groups_cleaned[
        "code original"
    ].apply(get_code_group_digits, digit_number=4)
    code_groups_cleaned["code_group_five"] = code_groups_cleaned[
        "code original"
    ].apply(get_code_group_digits, digit_number=5)
    code_groups_cleaned["code_group_six"] = code_groups_cleaned[
        "code original"
    ].apply(get_code_group_digits, digit_number=6)
    return


@app.cell
def _(code_groups_cleaned):
    code_groups_cleaned
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### merge experiments""")
    return


@app.cell
def _(six_digit_codes):
    six_digit_codes
    return


@app.cell
def _(get_code_group_digits, six_digit_codes):
    word_to_number = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}

    all_codes = six_digit_codes.copy()
    all_codes["six_digit_code"] = all_codes["NAICS22"]

    for column_prefix, digits in word_to_number.items():
        all_codes[f"{column_prefix}_digit_code"] = all_codes["NAICS22"].apply(
            get_code_group_digits, digit_number=digits
        )

    all_codes
    return all_codes, word_to_number


@app.cell
def _(all_codes, code_groups_cleaned):
    all_codes_merged = all_codes.merge(
        code_groups_cleaned[["2022 NAICS US Title", "code original"]],
        how="left",
        left_on="six_digit_code",
        right_on="code original",
    )
    all_codes_merged.rename(
        columns={
            "2022 NAICS US Title": "six_digit_group_title",
            "code original": "six_digit_title",
        },
        inplace=True,
    )

    all_codes_merged = all_codes_merged.merge(
        code_groups_cleaned[["2022 NAICS US Title", "code original"]],
        how="left",
        left_on="five_digit_code",
        right_on="code original",
    )
    all_codes_merged.rename(
        columns={
            "2022 NAICS US Title": "five_digit_group_title",
            "code original": "five_digit_title",
        },
        inplace=True,
    )

    all_codes_merged = all_codes_merged.merge(
        code_groups_cleaned[["2022 NAICS US Title", "code original"]],
        how="left",
        left_on="four_digit_code",
        right_on="code original",
    )
    all_codes_merged.rename(
        columns={
            "2022 NAICS US Title": "four_digit_group_title",
            "code original": "four_digit_title",
        },
        inplace=True,
    )

    all_codes_merged = all_codes_merged.merge(
        code_groups_cleaned[["2022 NAICS US Title", "code original"]],
        how="left",
        left_on="three_digit_code",
        right_on="code original",
    )
    all_codes_merged.rename(
        columns={
            "2022 NAICS US Title": "three_digit_group_title",
            "code original": "three_digit_title",
        },
        inplace=True,
    )

    all_codes_merged
    return (all_codes_merged,)


@app.cell
def _(all_codes_merged):
    all_codes_merged
    return


@app.cell
def _(code_groups_cleaned, pd, word_to_number):
    def merge_all_use_groups(six_digit_codes: pd.DataFrame, code_groups: pd.DataFrame) -> pd.DataFrame:
        all_codes_merged = six_digit_codes.merge(
            code_groups[["code original", "2022 NAICS US Title"]],
            how="left",
            left_on="six_digit_code",
            right_on="code original",
        )
        all_codes_merged.rename(
            columns={
                "INDEX ITEM DESCRIPTION": "NAICS22 Title",
                "2022 NAICS US Title": "six_digit_group_title",
                "code original": "six_digit",
            },
            inplace=True,
        )
        for digit_word in word_to_number.keys():
            print(digit_word)
            all_codes_merged = all_codes_merged.merge(
                code_groups_cleaned[["code original", "2022 NAICS US Title"]],
                how="left",
                left_on=f"{digit_word}_digit_code",
                right_on="code original",
            )
            all_codes_merged.rename(
                columns={
                    "2022 NAICS US Title": f"{digit_word}_digit_group_title",
                    "code original": f"{digit_word}_digit",
                },
                inplace=True,
            )
        return all_codes_merged
    return (merge_all_use_groups,)


@app.cell
def _(all_codes, code_groups_cleaned, merge_all_use_groups):
    use_grouped_merged = merge_all_use_groups(all_codes, code_groups_cleaned)
    use_grouped_merged
    return (use_grouped_merged,)


@app.cell
def _():
    # all_codes_merged[all_codes_merged["code original"].isnull()]
    return


@app.cell
def _(use_grouped_merged):
    use_grouped_merged.rename(
        columns={
            "NAICS22": "NAICS Code",
            "NAICS22 Title": "NAICS Title",
            "five_digit_code": "Five-digit Group Code",
            "five_digit_group_title": "Five-digit Group Title",
            "four_digit_code": "Four-digit Group Code",
            "four_digit_group_title": "Four-digit Group Title",
            "three_digit_code": "Three-digit Group Code",
            "three_digit_group_title": "Three-digit Group Title",
            "two_digit_code": "Two-digit Group Code",
            "two_digit_group_title": "Two-digit Group Title",
        },
        inplace=True,
    )
    return


@app.cell
def _(use_grouped_merged):
    naics_codes_output = use_grouped_merged[
        [
            "NAICS Code",
            "NAICS Title",
            "Five-digit Group Code",
            "Five-digit Group Title",
            "Four-digit Group Code",
            "Four-digit Group Title",
            "Three-digit Group Code",
            "Three-digit Group Title",
            "Two-digit Group Code",
            "Two-digit Group Title",
        ]
    ]
    return (naics_codes_output,)


@app.cell
def _(naics_codes_output):
    naics_codes_output
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Export processed NAICS codes""")
    return


@app.cell
def _(OUTPUT_DIRECTORY, code_groups_cleaned, naics_codes_output):
    naics_codes_output.to_csv(
        OUTPUT_DIRECTORY / "for_query_tool" / "naics_codes.csv", index=False
    )
    code_groups_cleaned.to_csv(
        OUTPUT_DIRECTORY / "naics_codes_cleaned.csv", index=False
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Explore Use Group data""")
    return


@app.cell
def _(use_groups_output):
    use_groups = use_groups_output.copy()
    use_groups
    return (use_groups,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Explore Use Group and NAICS overlap""")
    return


@app.cell
def _(code_groups_cleaned):
    naics_codes = code_groups_cleaned.copy()
    naics_codes
    return (naics_codes,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Not all not Use Groups have declared associations with NAICS codes""")
    return


@app.cell
def _(use_groups):
    use_groups_with_codes = use_groups[~use_groups["Use NAICS Code"].isna()]
    use_groups_with_codes
    return (use_groups_with_codes,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Do all NAICS codes in Use Group data appear in the NAICS code data?""")
    return


@app.cell
def _(naics_codes, use_groups_with_codes):
    uses_codes_joined = use_groups_with_codes.merge(
        naics_codes, how="left", left_on="Use NAICS Code", right_on="code original"
    )
    uses_codes_joined
    return (uses_codes_joined,)


@app.cell
def _(uses_codes_joined):
    uses_codes_joined_no_join = uses_codes_joined[
        uses_codes_joined["code original"].isna()
    ]
    uses_codes_joined_no_join
    return (uses_codes_joined_no_join,)


@app.cell
def _(uses_codes_joined_no_join):
    uses_codes_joined_no_join["Use NAICS Code"].value_counts()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""NACICS values in Use Group data that are lists can't simply be joined to the NAICS Codes data""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Look at specific use groups""")
    return


@app.cell
def _(uses_codes_joined):
    use_district_focus = ("Textile mills (313)", "R1")

    uses_codes_joined_use_district_focus = uses_codes_joined[
        (uses_codes_joined["Use Name"] == use_district_focus[0])
        & (uses_codes_joined["Zoning District"] == use_district_focus[1])
    ]
    uses_codes_joined_use_district_focus
    return (uses_codes_joined_use_district_focus,)


@app.cell
def _(mo):
    mo.md(r"""Can three-digit codes from Use Group data be linked to all relevant NAICS codes?""")
    return


@app.cell
def _(naics_codes, uses_codes_joined_use_district_focus):
    naics_codes[
        naics_codes["code_group_three"]
        == uses_codes_joined_use_district_focus.iloc[0]["code_group_three"]
    ]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Look at specific zoning districts""")
    return


@app.cell
def _(uses_codes_joined):
    uses_codes_joined["Zoning District"].value_counts()
    return


@app.cell
def _(uses_codes_joined):
    zoning_district_focus = "C1"

    uses_codes_joined_district_focus = uses_codes_joined[
        uses_codes_joined["Zoning District"] == zoning_district_focus
    ]
    uses_codes_joined_district_focus
    return (uses_codes_joined_district_focus,)


@app.cell
def _(uses_codes_joined_district_focus):
    uses_codes_joined_district_focus[uses_codes_joined_district_focus["Permitted"]]
    return


if __name__ == "__main__":
    app.run()

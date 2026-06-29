import pandas as pd


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
    permitted_district_uses = district_uses[~district_uses["Not permitted"]]

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
        matches = permitted_use_codes[permitted_use_codes.str.len() == length]
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
    if not "NAICS index names to include" in permitted_district_uses.columns:
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
            [item.strip() for sublist in split_names_to_include for item in sublist]
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
                lambda lst: [s.strip() for s in lst] if isinstance(lst, list) else lst
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
                    s.strip().isdigit() and len(s.strip()) <= drop_short_numeric_max_len
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
        district_uses["Use NAICS Code"].isin(permitted_use_codes["Permitted value"])
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
    exploded_exclusions = exploded_exclusions.explode("NAICS to subtract").reset_index(
        drop=True
    )

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

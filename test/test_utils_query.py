import pandas as pd
import numpy as np
from utils.query import (
    get_naics_indexes_by_district,
    get_all_uses_by_district,
    get_district_uses_by_naics_index,
)

pd.set_option("display.max_columns", None)


def test_get_naics_indexes_by_district():
    district_uses = pd.DataFrame(
        columns=[
            "Use Name",
            "Use NAICS Code",
            "NAICS to subtract",
            "NAICS index names to subtract",
            "Zoning District",
            "Not permitted",
            "Is Allowed",
        ],
        data=[
            ["A", "123", "12312, 123141", "", "A1", False, "Yes kinda"],
            ["B", "456", "456", "", "A1", True, "No"],
            ["A", "123", "12312, 123141", "", "A2", False, "Yes kinda"],
            ["B", "456", "456", "", "A2", True, "No"],
        ],
    )

    naics_codes = pd.DataFrame(
        columns=[
            "NAICS Code",
            "Five-digit Group Code",
            "Four-digit Group Code",
            "Three-digit Group Code",
            "NAICS Title",
        ],
        data=[
            ["123111", "12311", "1231", "123", "Shouldn't matter"],
            ["123121", "12312", "1231", "123", "Shouldn't matter"],
            ["123131", "12313", "1231", "123", "Shouldn't matter"],
            ["123141", "12314", "1231", "123", "Shouldn't matter"],
        ],
    )
    actual = get_naics_indexes_by_district(
        district_uses,
        "A1",
        naics_codes,
    )
    assert actual["Is Allowed"].to_list() == ["Yes kinda", "Yes kinda"]
    assert actual["NAICS Code"].to_list() == ["123111", "123131"]


def test_get_all_uses_by_district():
    district_uses = pd.DataFrame(
        columns=[
            "Use Name",
            "Use NAICS Code",
            "NAICS to subtract",
            "NAICS index names to subtract",
            "Zoning District",
            "Not permitted",
            "Is Allowed",
        ],
        data=[
            ["A", np.nan, np.nan, np.nan, "A1", False, "Yes of course"],
            ["B", "123", "12312, 123131", "", "A1", False, "Yes kinda"],
        ],
    )

    naics_codes = pd.DataFrame(
        columns=[
            "NAICS Code",
            "Five-digit Group Code",
            "Four-digit Group Code",
            "Three-digit Group Code",
            "NAICS Title",
        ],
        data=[
            ["123111", "12311", "1231", "123", "Shouldn't matter"],
            ["123121", "12312", "1231", "123", "Shouldn't matter"],
            ["123131", "12313", "1231", "123", "Shouldn't matter"],
        ],
    )
    actual = get_all_uses_by_district(
        district_uses,
        "A1",
        naics_codes,
    )
    print(actual["Permitted reason"])
    assert actual["Is Allowed"].to_list() == ["Yes of course", "Yes kinda"]
    assert actual["NAICS Code"].to_list() == ["", "123111"]


def test_get_naics_indexes_by_district_mock_m2(
    mock_uses_by_zoning_district: pd.DataFrame, mock_naics_codes: pd.DataFrame
):
    actual = get_naics_indexes_by_district(
        mock_uses_by_zoning_district,
        "M2",
        mock_naics_codes,
    )
    assert len(actual) == 733
    assert len(actual[actual["NAICS Code"] == "311512"]) == 5
    assert len(actual[actual["Four-digit Group Code"] == "3115"]) == 105
    assert len(actual[actual["NAICS Code"] == "311611"]) == 0
    assert len(actual[actual["Four-digit Group Code"] == "3116"]) == 0
    assert len(actual[actual["Four-digit Group Code"] == "3117"]) == 0


def test_get_naics_indexes_by_district_mock_c1(
    mock_uses_by_zoning_district: pd.DataFrame, mock_naics_codes: pd.DataFrame
):
    actual = get_naics_indexes_by_district(
        mock_uses_by_zoning_district,
        "C1",
        mock_naics_codes,
    )
    assert (
        len(mock_naics_codes[mock_naics_codes["Five-digit Group Code"] == "71399"])
        == 117
    )
    assert len(actual) == 110
    assert len(actual[actual["Permitted value"] == "71399"]) == 110
    assert len(actual[actual["NAICS Title"] == "Escape rooms"]) == 0


def test_get_district_uses_by_naics_index():
    district_uses = pd.DataFrame(
        columns=[
            "Use Name",
            "Use NAICS Code",
            "NAICS index names to include",
            "NAICS to subtract",
            "NAICS index names to subtract",
            "Zoning District",
            "Not permitted",
            "Is Allowed",
        ],
        data=[
            [
                "A use",
                "123",
                "Shouldn't matter",
                "12312, 123141",
                "Shouldn't matter either",
                "A1",
                False,
                "Yes",
            ],
            [
                "A use",
                "123",
                "Shouldn't matter",
                "12312, 123141",
                "Shouldn't matter either",
                "A2",
                False,
                "Yes pretty much",
            ],
            [
                "A use",
                "456",
                "Shouldn't matter",
                "456",
                "Shouldn't matter either",
                "A1",
                True,
                "No",
            ],
        ],
    )
    naics_codes = pd.DataFrame(
        columns=[
            "NAICS Code",
            "NAICS Title",
            "Five-digit Group Code",
            "Four-digit Group Code",
            "Three-digit Group Code",
        ],
        data=[
            ["123111", "Allowed in both", "12311", "1231", "123"],
            ["123112", "Something else", "12311", "1231", "123"],
        ],
    )
    naics_title = "Allowed in both"

    actual = get_district_uses_by_naics_index(district_uses, naics_codes, naics_title)
    expected = pd.DataFrame(
        columns=[
            "NAICS Title",
            "NAICS Code",
            "Use Name",
            "Zoning District",
            "Is Allowed",
            "Permitted reason",
            "Permitted value",
            "Five-digit Group Code",
            "Four-digit Group Code",
            "Three-digit Group Code",
            "Use NAICS Code",
            "NAICS index names to include",
            "NAICS to subtract",
            "NAICS index names to subtract",
            "Not permitted",
        ],
        data=[
            [
                "Allowed in both",
                "123111",
                "A use",
                "A1",
                "Yes",
                "Three-digit Group Code",
                "123",
                "12311",
                "1231",
                "123",
                "123",
                "Shouldn't matter",
                "12312, 123141",
                "Shouldn't matter either",
                False,
            ],
            [
                "Allowed in both",
                "123111",
                "A use",
                "A2",
                "Yes pretty much",
                "Three-digit Group Code",
                "123",
                "12311",
                "1231",
                "123",
                "123",
                "Shouldn't matter",
                "12312, 123141",
                "Shouldn't matter either",
                False,
            ],
        ],
    )

    pd.testing.assert_frame_equal(actual, expected)


def test_get_district_uses_by_naics_index_not_addressed():
    district_uses = pd.DataFrame(
        columns=[
            "Use NAICS Code",
            "NAICS index names to include",
            "NAICS to subtract",
            "NAICS index names to subtract",
            "Zoning District",
            "Not permitted",
            "Is Allowed",
        ],
        data=[
            ["123", "The only ZR use", "12312, 123141", "", "A1", False, "Yes"],
        ],
    )
    naics_codes = pd.DataFrame(
        columns=[
            "NAICS Code",
            "NAICS Title",
            "Five-digit Group Code",
            "Four-digit Group Code",
            "Three-digit Group Code",
        ],
        data=[
            ["345111", "Not in the ZR", "34511", "3451", "345"],
        ],
    )
    naics_title = "Not in the ZR"

    actual = get_district_uses_by_naics_index(district_uses, naics_codes, naics_title)

    assert actual.empty


def test_get_district_uses_by_naics_index_all_districts():
    district_uses = pd.DataFrame(
        columns=[
            "Use Group",
            "Use Header",
            "Use Name",
            "Use NAICS Code",
            "NAICS index names to include",
            "NAICS to subtract",
            "NAICS index names to subtract",
            "Zoning District",
            "Not permitted",
            "Is Allowed",
        ],
        data=[
            [
                "A group",
                "A header",
                "A use",
                "123",
                "Shouldn't matter",
                "12312, 123141",
                "Shouldn't matter either",
                "A1",
                False,
                "Yes",
            ],
            [
                "A group",
                "A header",
                "A use",
                "123",
                "Shouldn't matter",
                "12312, 123141",
                "Shouldn't matter either",
                "A2",
                True,
                "Nope",
            ],
        ],
    )
    naics_codes = pd.DataFrame(
        columns=[
            "NAICS Code",
            "NAICS Title",
            "Five-digit Group Code",
            "Four-digit Group Code",
            "Three-digit Group Code",
        ],
        data=[
            ["123111", "Allowed in A1", "12311", "1231", "123"],
        ],
    )
    naics_title = "Allowed in A1"

    actual = get_district_uses_by_naics_index(
        district_uses, naics_codes, naics_title, include_all_districts=True
    )

    assert len(actual) == 2
    assert actual["Zoning District"].unique().tolist() == ["A1", "A2"]

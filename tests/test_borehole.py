
import pandas as pd
import pytest

from src.borehole import (
    calculate_interval_thickness,
    identify_depth_gaps,
    validate_borehole_data,
)


@pytest.fixture
def sample_data():
    return pd.DataFrame([
        {
            "Borehole_ID": "BH-001",
            "From_m": 0.0,
            "To_m": 1.5,
            "Lithology": "Topsoil",
            "Rock_Colour": "Brown",
            "Weathering": "Highly Weathered",
            "Mineralization": "None",
            "Description": "Loose soil",
        },
        {
            "Borehole_ID": "BH-001",
            "From_m": 1.5,
            "To_m": 4.0,
            "Lithology": "Laterite",
            "Rock_Colour": "Red",
            "Weathering": "Highly Weathered",
            "Mineralization": "Goethite",
            "Description": "Lateritic material",
        },
        {
            "Borehole_ID": "BH-001",
            "From_m": 5.0,
            "To_m": 8.0,
            "Lithology": "BHQ",
            "Rock_Colour": "Grey",
            "Weathering": "Slightly Weathered",
            "Mineralization": "Hematite",
            "Description": "Banded hematite quartzite",
        },
    ])


def test_valid_data(sample_data):
    assert validate_borehole_data(sample_data) == []


def test_empty_dataset():
    assert "empty" in validate_borehole_data(
        pd.DataFrame()
    )[0].lower()


def test_missing_columns(sample_data):
    sample_data = sample_data.drop(columns=["Lithology"])

    errors = validate_borehole_data(sample_data)

    assert any("Missing required columns" in e for e in errors)


def test_negative_depth(sample_data):
    sample_data.loc[0, "From_m"] = -1.0

    errors = validate_borehole_data(sample_data)

    assert any("negative" in e.lower() for e in errors)


def test_invalid_depth_order(sample_data):
    sample_data.loc[0, "From_m"] = 2.0
    sample_data.loc[0, "To_m"] = 1.0

    errors = validate_borehole_data(sample_data)

    assert any("less than" in e for e in errors)


def test_non_numeric_depth(sample_data):
    sample_data["From_m"] = sample_data["From_m"].astype(object)
    sample_data.loc[0, "From_m"] = "unknown"

    errors = validate_borehole_data(sample_data)

    assert any("numeric" in e.lower() for e in errors)


def test_overlapping_intervals(sample_data):
    sample_data.loc[1, "From_m"] = 1.0

    errors = validate_borehole_data(sample_data)

    assert any("overlapping" in e.lower() for e in errors)


def test_calculate_interval_thickness(sample_data):
    result = calculate_interval_thickness(sample_data)

    assert result.loc[0, "Thickness_m"] == pytest.approx(1.5)
    assert result.loc[1, "Thickness_m"] == pytest.approx(2.5)
    assert result.loc[2, "Thickness_m"] == pytest.approx(3.0)


def test_gap_detection(sample_data):
    gaps = identify_depth_gaps(sample_data)

    assert len(gaps) == 1
    assert gaps.iloc[0]["Borehole_ID"] == "BH-001"
    assert gaps.iloc[0]["Gap_From_m"] == pytest.approx(4.0)
    assert gaps.iloc[0]["Gap_To_m"] == pytest.approx(5.0)
    assert gaps.iloc[0]["Gap_Thickness_m"] == pytest.approx(1.0)


def test_no_gap_detection(sample_data):
    continuous_data = sample_data.iloc[:2].copy()

    gaps = identify_depth_gaps(continuous_data)

    assert gaps.empty


def test_invalid_data_raises_error(sample_data):
    sample_data.loc[0, "From_m"] = -1.0

    with pytest.raises(ValueError):
        calculate_interval_thickness(sample_data)

    with pytest.raises(ValueError):
        identify_depth_gaps(sample_data)

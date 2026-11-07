
"""Core data validation and processing for geological borehole logs."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = [
    "Borehole_ID",
    "From_m",
    "To_m",
    "Lithology",
    "Rock_Colour",
    "Weathering",
    "Mineralization",
    "Description",
]


def validate_borehole_data(data: pd.DataFrame) -> list[str]:
    """Return validation errors found in borehole interval data."""
    errors: list[str] = []

    if not isinstance(data, pd.DataFrame):
        return ["Input must be a pandas DataFrame."]

    if data.empty:
        return ["Borehole dataset is empty."]

    missing = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing:
        return [f"Missing required columns: {', '.join(missing)}"]

    if data[["Borehole_ID", "Lithology"]].isna().any().any():
        errors.append("Borehole_ID and Lithology cannot be empty.")

    if data[["From_m", "To_m"]].isna().any().any():
        errors.append("Depth values cannot be empty.")

    depths = data[["From_m", "To_m"]].apply(
        pd.to_numeric, errors="coerce"
    )

    if depths.isna().any().any():
        errors.append("From_m and To_m must contain numeric values.")
        return errors

    if (depths < 0).any().any():
        errors.append("Depth values cannot be negative.")

    if (depths["From_m"] >= depths["To_m"]).any():
        errors.append("Each interval must have From_m less than To_m.")

    if errors:
        return errors

    checked = data.copy()
    checked["From_m"] = depths["From_m"]
    checked["To_m"] = depths["To_m"]

    for borehole_id, group in checked.groupby("Borehole_ID"):
        group = group.sort_values("From_m")
        previous_end = None

        for _, row in group.iterrows():
            if previous_end is not None:
                if row["From_m"] < previous_end:
                    errors.append(
                        f"Overlapping intervals detected in {borehole_id}."
                    )
                    break

            previous_end = row["To_m"]

    return errors


def calculate_interval_thickness(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the dataset with interval thickness in metres."""
    errors = validate_borehole_data(data)

    if errors:
        raise ValueError("; ".join(errors))

    result = data.copy()
    result["From_m"] = pd.to_numeric(result["From_m"])
    result["To_m"] = pd.to_numeric(result["To_m"])
    result["Thickness_m"] = result["To_m"] - result["From_m"]

    return result


def identify_depth_gaps(data: pd.DataFrame) -> pd.DataFrame:
    """Identify gaps between consecutive intervals in each borehole."""
    errors = validate_borehole_data(data)

    if errors:
        raise ValueError("; ".join(errors))

    gaps = []

    for borehole_id, group in data.groupby("Borehole_ID"):
        group = group.sort_values("From_m")
        previous_end = None

        for _, row in group.iterrows():
            start = float(row["From_m"])
            end = float(row["To_m"])

            if previous_end is not None and start > previous_end:
                gaps.append({
                    "Borehole_ID": borehole_id,
                    "Gap_From_m": previous_end,
                    "Gap_To_m": start,
                    "Gap_Thickness_m": start - previous_end,
                })

            previous_end = end

    return pd.DataFrame(
        gaps,
        columns=[
            "Borehole_ID",
            "Gap_From_m",
            "Gap_To_m",
            "Gap_Thickness_m",
        ],
    )

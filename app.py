
"""Interactive geological borehole log visualizer."""

from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from src.borehole import (
    REQUIRED_COLUMNS,
    calculate_interval_thickness,
    identify_depth_gaps,
    validate_borehole_data,
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Geological Borehole Log Visualizer",
    page_icon="⛏️",
    layout="wide",
)

st.title("⛏️ Geological Borehole Log Visualizer")
st.caption(
    "Interactive geological interval logging, visualization "
    "and depth analysis."
)

st.info(
    "Demonstration project: the included sample dataset is synthetic "
    "and does not represent actual mine drilling records."
)


# --------------------------------------------------
# Lithology colour configuration
# --------------------------------------------------

LITHOLOGY_COLORS = {
    "Topsoil": "#A67C52",
    "Laterite": "#C65D32",
    "Weathered Shale": "#B8A58A",
    "BHQ": "#9CA3AF",
    "Banded Hematite Quartzite": "#8B929A",
    "Hematite Ore": "#8B1E1E",
    "Fresh Quartzite": "#E5E7EB",
    "Quartzite": "#D6D3D1",
    "Iron Ore": "#991B1B",
    "Shale": "#64748B",
    "Sandstone": "#D6A85F",
    "Granite": "#C08497",
}


def get_lithology_color(lithology: str) -> str:
    """Return configured colour or a neutral fallback."""
    return LITHOLOGY_COLORS.get(lithology, "#60A5FA")


# --------------------------------------------------
# Data loading
# --------------------------------------------------

@st.cache_data
def load_sample_data() -> pd.DataFrame:
    """Load the bundled synthetic sample dataset."""
    return pd.read_csv("data/sample/borehole_sample.csv")


def load_uploaded_file(uploaded_file) -> pd.DataFrame:
    """Read uploaded CSV or Excel data."""
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    if filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)

    raise ValueError("Unsupported file format.")


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Data Source")

data_source = st.sidebar.radio(
    "Choose dataset",
    ["Sample Dataset", "Upload Your Dataset"],
)

try:
    if data_source == "Sample Dataset":
        data = load_sample_data()
        st.sidebar.success("Synthetic sample data loaded.")

    else:
        uploaded_file = st.sidebar.file_uploader(
            "Upload borehole data",
            type=["csv", "xlsx", "xls"],
        )

        if uploaded_file is None:
            st.info(
                "Upload a CSV or Excel borehole dataset "
                "to begin visualization."
            )
            st.stop()

        data = load_uploaded_file(uploaded_file)
        st.sidebar.success("Uploaded dataset loaded.")

except Exception as error:
    st.error(f"Could not load dataset: {error}")
    st.stop()


# --------------------------------------------------
# Validation
# --------------------------------------------------

errors = validate_borehole_data(data)

if errors:
    st.error("Dataset validation failed.")

    for error in errors:
        st.write(f"- {error}")

    st.stop()

st.success("Dataset validation passed.")

processed_data = calculate_interval_thickness(data)
gaps = identify_depth_gaps(data)


# --------------------------------------------------
# Dataset overview
# --------------------------------------------------

st.header("Dataset Overview")

total_boreholes = processed_data["Borehole_ID"].nunique()
total_intervals = len(processed_data)
total_lithologies = processed_data["Lithology"].nunique()
total_gaps = len(gaps)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Boreholes", total_boreholes)
col2.metric("Intervals", total_intervals)
col3.metric("Lithologies", total_lithologies)
col4.metric("Depth Gaps", total_gaps)

st.divider()


# --------------------------------------------------
# Borehole selection
# --------------------------------------------------

st.header("Borehole Geological Log")

borehole_ids = sorted(
    processed_data["Borehole_ID"].unique()
)

selected_boreholes = st.multiselect(
    "Select borehole(s)",
    options=borehole_ids,
    default=borehole_ids[:1],
)

if not selected_boreholes:
    st.warning("Select at least one borehole.")
    st.stop()

selected_data = processed_data[
    processed_data["Borehole_ID"].isin(selected_boreholes)
].copy()



# --------------------------------------------------
# Geological log visualization
# --------------------------------------------------

import plotly.graph_objects as go

fig = go.Figure()

for borehole_id in selected_boreholes:
    borehole_data = selected_data[
        selected_data["Borehole_ID"] == borehole_id
    ].sort_values("From_m")

    for _, row in borehole_data.iterrows():
        lithology = row["Lithology"]
        color = get_lithology_color(lithology)

        customdata = [[
            row["From_m"],
            row["To_m"],
            row["Thickness_m"],
            row["Rock_Colour"],
            row["Weathering"],
            row["Mineralization"],
            row["Description"],
        ]]

        fig.add_trace(
            go.Bar(
                x=[row["Thickness_m"]],
                y=[borehole_id],
                base=[row["From_m"]],
                orientation="h",
                name=lithology,
                legendgroup=lithology,
                showlegend=not any(
                    trace.name == lithology
                    for trace in fig.data
                ),
                marker=dict(
                    color=color,
                    line=dict(color="#FFFFFF", width=0.7),
                ),
                customdata=customdata,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Lithology: " + lithology + "<br>"
                    "From: %{customdata[0]:.2f} m<br>"
                    "To: %{customdata[1]:.2f} m<br>"
                    "Thickness: %{customdata[2]:.2f} m<br>"
                    "Rock colour: %{customdata[3]}<br>"
                    "Weathering: %{customdata[4]}<br>"
                    "Mineralization: %{customdata[5]}<br>"
                    "Description: %{customdata[6]}"
                    "<extra></extra>"
                ),
            )
        )

fig.update_layout(
    title="Lithological Intervals by Borehole",
    height=max(450, 180 * len(selected_boreholes)),
    barmode="overlay",
    xaxis=dict(
        title="Depth (m)",
        side="top",
        type="linear",
        rangemode="tozero",
    ),
    yaxis=dict(
        title="Borehole",
        autorange="reversed",
    ),
    legend_title="Lithology",
    hoverlabel=dict(align="left"),
    margin=dict(l=60, r=40, t=90, b=50),
)

st.plotly_chart(fig, use_container_width=True)


st.caption(
    "Each coloured interval represents a logged lithological unit. "
    "Hover over an interval to inspect its geological attributes."
)


# --------------------------------------------------
# Borehole depth summary
# --------------------------------------------------

st.header("Borehole Depth Summary")

depth_summary = (
    selected_data.groupby("Borehole_ID")
    .agg(
        Start_Depth_m=("From_m", "min"),
        End_Depth_m=("To_m", "max"),
        Total_Logged_Thickness_m=("Thickness_m", "sum"),
        Number_of_Intervals=("Lithology", "count"),
    )
    .reset_index()
)

depth_summary["Depth_Range_m"] = (
    depth_summary["End_Depth_m"]
    - depth_summary["Start_Depth_m"]
)

st.dataframe(
    depth_summary.round(2),
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Lithology distribution
# --------------------------------------------------

st.header("Lithology Distribution")

distribution = (
    selected_data.groupby("Lithology")["Thickness_m"]
    .sum()
    .reset_index()
    .sort_values("Thickness_m", ascending=False)
)

distribution.columns = ["Lithology", "Total_Thickness_m"]

fig_distribution = px.bar(
    distribution,
    x="Lithology",
    y="Total_Thickness_m",
    color="Lithology",
    color_discrete_map=LITHOLOGY_COLORS,
    title="Total Logged Thickness by Lithology",
)

fig_distribution.update_layout(
    showlegend=False,
    xaxis_title="Lithology",
    yaxis_title="Thickness (m)",
)

st.plotly_chart(
    fig_distribution,
    use_container_width=True,
)


# --------------------------------------------------
# Depth gap analysis
# --------------------------------------------------

st.header("Depth Gap Analysis")

selected_gaps = gaps[
    gaps["Borehole_ID"].isin(selected_boreholes)
]

if selected_gaps.empty:
    st.success("No depth gaps detected in the selected boreholes.")

else:
    st.warning(
        f"{len(selected_gaps)} depth gap(s) detected."
    )

    st.dataframe(
        selected_gaps.round(2),
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# Detailed geological interval table
# --------------------------------------------------

st.header("Detailed Geological Log Data")

st.dataframe(
    selected_data.sort_values(
        ["Borehole_ID", "From_m"]
    ).round(2),
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Export options
# --------------------------------------------------

st.header("Export Results")

csv_data = selected_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Geological Log (CSV)",
    data=csv_data,
    file_name="geological_borehole_log.csv",
    mime="text/csv",
)

excel_buffer = BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl",
) as writer:
    selected_data.to_excel(
        writer,
        sheet_name="Borehole_Log",
        index=False,
    )

    depth_summary.to_excel(
        writer,
        sheet_name="Depth_Summary",
        index=False,
    )

    selected_gaps.to_excel(
        writer,
        sheet_name="Depth_Gaps",
        index=False,
    )

st.download_button(
    label="Download Geological Report (Excel)",
    data=excel_buffer.getvalue(),
    file_name="geological_borehole_report.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
)

st.divider()

st.caption(
    "Geological Borehole Log Visualizer | "
    "Python · Pandas · Plotly · Streamlit"
)

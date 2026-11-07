
# Geological Borehole Log Visualizer

An interactive Python application for validating, processing, analyzing, and visualizing geological borehole interval data.

Built with Python, Pandas, Plotly, and Streamlit.

## Features

- Import borehole data from CSV and Excel files.
- Validate geological interval records.
- Visualize lithological units against depth.
- Compare multiple boreholes.
- Calculate interval thickness automatically.
- Detect gaps between consecutive geological intervals.
- Summarize borehole depth and lithological distribution.
- Export processed geological logs as CSV and Excel reports.

## Technology Stack

- Python 3.12
- Pandas
- NumPy
- Plotly
- Streamlit
- OpenPyXL
- Pytest

## Project Structure

```text
Geological-Borehole-Log-Visualizer/
│
├── data/
│   └── sample/
│       └── borehole_sample.csv
│
├── docs/
│   └── images/
│
├── outputs/
│
├── src/
│   ├── __init__.py
│   └── borehole.py
│
├── tests/
│   ├── __init__.py
│   └── test_borehole.py
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/Geological-Borehole-Log-Visualizer.git
cd Geological-Borehole-Log-Visualizer
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

## Run Automated Tests

```bash
pytest -v
```

The current test suite contains 11 automated tests covering data validation, interval thickness calculations, overlap detection, and depth gap identification.

## Input Data Format

The application requires the following columns:

| Column | Description |
|---|---|
| Borehole_ID | Unique borehole identifier |
| From_m | Starting depth in metres |
| To_m | Ending depth in metres |
| Lithology | Geological rock unit |
| Rock_Colour | Observed rock colour |
| Weathering | Weathering condition |
| Mineralization | Mineralization observations |
| Description | Geological interval description |

## Geological Applications

The tool demonstrates workflows relevant to:

- Geological and lithological logging.
- Mineral exploration.
- Iron ore exploration.
- Borehole interval analysis.
- Geological data quality control.
- Exploration data visualization.

## Data Disclaimer

The included borehole dataset is synthetic and created exclusively for software demonstration and testing.

It does not represent actual drilling records, geological observations, or exploration results from Bolani Ores Mines or any other mining project.

Interpretations generated from uploaded datasets depend on the quality and accuracy of the supplied geological records.

## Current Development Status

- [x] Borehole data validation
- [x] Interval thickness calculation
- [x] Depth gap detection
- [x] Interactive lithological visualization
- [x] Multiple borehole selection
- [x] CSV and Excel import
- [x] CSV and Excel export
- [x] Automated core-function tests
- [ ] GitHub Actions CI
- [ ] Cloud deployment

## License

MIT License

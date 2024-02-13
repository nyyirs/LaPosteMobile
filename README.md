# LaPosteMobile Data Plan Comparison Tool

## Overview
The LaPosteMobile Data Plan Comparison Tool is a Python-based application designed to aggregate and compare mobile data plans from various providers in France.

## Features
- **Data Plan Extraction**: Extracts mobile plan details and pricing information from different mobile providers.
- **Data Normalization**: Converts data units to a uniform measurement (megabytes) for easy comparison.
- **Data Aggregation**: Merges data from multiple sources into a single DataFrame for analysis.
- **Excel Export**: Outputs the comparison results into an Excel file, with options to format the output for better readability.

## How It Works
The tool uses Python scripts to scrape mobile plan data from the web, process this information, and compile it into an organized format. The main components of the tool include:
- `main.py`: The entry point of the application, orchestrating the data extraction, processing, and export.
- `modules/`: A directory containing Python modules for each mobile provider. Each module is responsible for extracting data specific to its provider.

### Data Extraction and Processing
Each module within the `modules/` directory uses either web scraping techniques or API calls to retrieve mobile plan data from the respective provider's website. The data is then normalized to ensure consistency across different units of measurement.

### Output
The aggregated data is exported to an Excel file (`Results.xlsx`), where users can easily compare different mobile plans. The Excel file includes bold headers for clarity and organizes the data plans by provider, making it straightforward to identify the best option.

## Getting Started
To use this tool, you will need Python installed on your machine along with the required libraries listed in `requirements.txt`.

1. Clone the repository to your local machine.
2. Install the required Python packages using `pip install -r requirements.txt`.
3. Run `python src/main.py` to start the data extraction and comparison process.
4. Open the generated `Results.xlsx` file to view the comparison results.

## Dependencies
- Python 3.x
- pandas
- requests
- BeautifulSoup4
- selenium
- lxml
- xlsxwriter

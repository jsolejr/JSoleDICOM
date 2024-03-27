# Simple Study Count (SimpleStudyCount.py)

The `SimpleStudyCount.py` script is designed to query a PACS server for DICOM studies and log each study's accession number and Study Instance UID to a CSV file. This tool can be particularly useful for auditing and tracking studies in a PACS environment.

## Requirements

- Python 3.6 or higher
- pynetdicom: `pip install pynetdicom`
- pydicom: `pip install pydicom`

## Configuration

Before running the script, ensure you configure the following variables within the script according to your PACS server details:

- `calling_aet`: The AE Title of your DICOM application.
- `called_aet`: The AE Title of the PACS server you're querying.
- `pacs_host`: The hostname or IP address of the PACS server.
- `pacs_port`: The port number on which the PACS server is listening.

## Usage

1. Open a terminal or command prompt.
2. Navigate to the directory containing `SimpleStudyCount.py`.
3. Run the script using Python:

    ```bash
    python SimpleStudyCount.py
    ```

The script will start querying the PACS server based on the specified date range and write the accession numbers and Study Instance UIDs to a CSV file named `dicom_query_results.csv`.

## Output

The output CSV file will contain the following columns:

- `Accession Number`: The unique identifier for each study.
- `Study UID`: The unique DICOM identifier for each study.

You can find the `dicom_query_results.csv` file in the same directory as the `SimpleStudyCount.py` script after the script finishes running.

## Notes

- Ensure your PACS server and network settings allow queries from your application's AE Title.
- Modify the date range within the script as needed for your specific query requirements.
- The script is configured to query studies within hourly blocks for the specified date range to manage performance and load on the PACS server.

# Discovery Tool

The `discovery_tool.py` script facilitates the discovery phase of DICOM data migration projects. It queries PACS servers for study details within a specified date range, focusing particularly on studies that may lack comprehensive metadata such as a Study Description. This tool is invaluable for identifying and cataloging studies that require further attention or specific handling during migration processes.

## Features

- **DICOM C-FIND Operation**: Utilizes the C-FIND operation to query PACS servers for study details.
- **Study Description Filter**: Specifically logs studies that lack a Study Description, which may indicate incomplete metadata.
- **Configurable Date Range**: Allows users to specify the start and end dates for the query, enabling targeted data retrieval.
- **Hourly Query Segmentation**: Breaks down queries into hourly intervals to manage and mitigate load on the PACS server.

## Prerequisites

- **Python 3.6+**: Ensure Python 3.6 or newer is installed on your system.
- **Required Libraries**:
  - `pydicom`: For handling DICOM data structures and files.
  - `pynetdicom`: For performing DICOM network operations.

## Setup Instructions

1. **Install Required Libraries**: If not already installed, you can install the required Python packages by running:

    ```bash
    pip install pydicom pynetdicom
    ```

2. **Configure Script Settings**: Edit `migration_discovery_tool.py` to set up the necessary PACS connection details and AE titles:

    - `calling_aet`: Your DICOM Application Entity Title.
    - `called_aet`: The PACS server's Application Entity Title.
    - `pacs_host`: The IP address or hostname of the PACS server.
    - `pacs_port`: The network port the PACS server uses for connections.

## How to Use

1. Open your terminal or command prompt.
2. Navigate to the directory where `migration_discovery_tool.py` is located.
3. Execute the script by running:

    ```bash
    python discovery_tool.py
    ```

The script will initiate queries to the PACS server for studies conducted within the specified date range. Studies identified without a Study Description will be logged into a CSV file, `dicom_query_results.csv`, with pertinent details for each study.

## Output Format

The generated `dicom_query_results.csv` will include columns for:

- `Accession Number`: The unique identifier assigned to each study.
- `Study Date`: The date when the study was performed.
- `Study Time`: The time range during which the study took place.
- `Patient ID`: The identifier used for the patient in the study.
- `Study UID`: The unique DICOM identifier for the study.
- `Study Description`: The descriptive text of the study (entries in this column will be empty for the studies of interest).

## Additional Notes

- The date range for the query (`start_date` and `end_date`) can be adjusted within the script to focus on a specific timeframe.
- Queries are segmented into hourly blocks to efficiently manage the load on the PACS server and ensure smooth operation.


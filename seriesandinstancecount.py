import pydicom
from pynetdicom import AE, QueryRetrievePresentationContexts
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind
import csv
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pynetdicom')
logger.setLevel(logging.INFO)

# Define the Calling and Called AE Titles
calling_aet = 'calling_ae'
called_aet = 'called_ae'

# Initialise the Application Entity with the Calling AE Title
ae = AE(ae_title=calling_aet)
ae.requested_contexts = QueryRetrievePresentationContexts

# Replace with the correct PACS details
pacs_host = 'IP/Hostname'
pacs_port = PORT

# Define the start date as January 1st, 2014
start_date = datetime(2014, 1, 1)

# Define the end date as the current date and time
end_date = datetime.now()

# Open CSV file for output
with open('dicom_series_instance_counts.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Accession Number', 'Series Count', 'Instance Count'])

    current_date = start_date
    while current_date < end_date:
        for i in range(24):  # 24 blocks for 1-hour intervals in a day
            block_start = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=i)
            block_end = block_start + timedelta(hours=1)

            assoc = ae.associate(pacs_host, pacs_port, ae_title=called_aet)
            if assoc.is_established:
                logging.info(f"Association established for time block {block_start} to {block_end}")

                # Modify the query dataset
                ds = pydicom.Dataset()
                ds.QueryRetrieveLevel = 'STUDY'
                ds.StudyDate = block_start.strftime('%Y%m%d')
                # Query for Accession Number, Series and SOP Instance UIDs
                ds.AccessionNumber = ''
                ds.SeriesInstanceUID = ''
                ds.SOPInstanceUID = ''

                # Send query
                responses = assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)

                results = {}
                for (status, identifier) in responses:
                    if status and status.Status in (0xFF00, 0xFF01) and identifier:
                        accession_number = identifier.get('AccessionNumber', '')
                        series_uid = identifier.get('SeriesInstanceUID', '')
                        sop_instance_uid = identifier.get('SOPInstanceUID', '')

                        # Accumulate counts by accession number
                        if accession_number:
                            if accession_number not in results:
                                results[accession_number] = {'series': set(), 'instances': set()}
                            results[accession_number]['series'].add(series_uid)
                            results[accession_number]['instances'].add(sop_instance_uid)

                # After processing all responses, write the counts to the CSV
                for accession_number, counts in results.items():
                    series_count = len(counts['series'])
                    instance_count = len(counts['instances'])
                    writer.writerow([accession_number, series_count, instance_count])

                assoc.release()
                logging.info("Association released")
                # Consider a sleep here if needed

            else:
                logging.info(f"Association with PACS failed for time block {block_start} to {block_end}")

        current_date += timedelta(days=1)

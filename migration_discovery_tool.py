import pydicom
from pynetdicom import AE, QueryRetrievePresentationContexts
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind
import csv
import logging
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pynetdicom')
logger.setLevel(logging.INFO)

# Define the Calling and Called AE Titles
calling_aet = 'SeibertWork'
called_aet = 'DICOM_QRP'

# Initialise the Application Entity with the Calling AE Title
ae = AE(ae_title=calling_aet)
ae.requested_contexts = QueryRetrievePresentationContexts

# Replace with the correct PACS details
pacs_host = '152.79.9.53'
pacs_port = 107

# Define the start date as January 1st, 2014
start_date = datetime(2014, 1, 1)

# Define the end date as the current date and time
end_date = datetime.now()

# Open a CSV file to write the results.  Currently this will only record exams that return with no Study Description, which was a specific use case for the last use case.
with open('dicom_query_results.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Accession Number', 'Study Date', 'Study Time', 'Patient ID', 'Study UID', 'Study Description'])

    current_date = start_date
    while current_date < end_date:
        for i in range(24):  # 24 blocks for 1-hour intervals in a day
            block_start = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=i)
            block_end = block_start + timedelta(hours=1)

            # Establish association
            assoc = ae.associate(pacs_host, pacs_port, ae_title=called_aet)
            if assoc.is_established:
                logging.info(f"Association established for time block {block_start} to {block_end}")

                # Create a DICOM Dataset for each query
                ds = pydicom.Dataset()
                ds.QueryRetrieveLevel = 'STUDY'
                ds.StudyDate = block_start.strftime('%Y%m%d')
                ds.StudyTime = block_start.strftime('%H%M%S') + '-' + block_end.strftime('%H%M%S')
                ds.AccessionNumber = ''
                ds.PatientID = ''
                ds.StudyInstanceUID = ''
                ds.StudyDescription = ''

                responses = assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)
                num_results = 0
                for (status, identifier) in responses:
                    if status and status.Status in (0xFF00, 0xFF01) and identifier:
                        # Check if StudyDescription is empty
                        if identifier.get('StudyDescription', '') == '':  # Currently this will only record exams that return with no Study Description, which was a specific use case for the last use case.
                            # Write the data to the CSV file
                            writer.writerow([
                                identifier.AccessionNumber or '',
                                identifier.StudyDate or '',
                                identifier.StudyTime or '',
                                identifier.PatientID or '',
                                identifier.StudyInstanceUID or '',
                                identifier.get('StudyDescription', '')
                            ])
                            num_results += 1

                logging.info(f"Query complete. Number of results: {num_results}")
                assoc.release()
                logging.info("Association released")

                # Wait for 2 seconds after the association is closed
                #time.sleep(2)
            else:
                logging.info(f"Association with PACS failed for time block {block_start} to {block_end}")

        current_date += timedelta(days=1)

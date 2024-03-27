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
calling_aet = 'YOUR_CALLING_AE_TITLE'
called_aet = 'YOUR_CALLED_AE_TITLE'

# Initialize the Application Entity with the Calling AE Title
ae = AE(ae_title=calling_aet)
ae.requested_contexts = QueryRetrievePresentationContexts

# Replace with the correct PACS details
pacs_host = 'PACS_IP_OR_HOSTNAME'
pacs_port = PACS_PORT  # Replace PACS_PORT with the actual port number

# Define the date range for your query
start_date = datetime(2014, 1, 1)  # Example start date
end_date = datetime.now()  # Current date and time as the end date

# Open a CSV file to write the results
with open('dicom_query_results.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Accession Number', 'Study UID'])

    current_date = start_date
    while current_date < end_date:
        for i in range(24):  # Iterate over each hour of the current day
            block_start = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=i)
            block_end = block_start + timedelta(hours=1)

            # Establish association with PACS
            assoc = ae.associate(pacs_host, pacs_port, ae_title=called_aet)
            if assoc.is_established:
                logging.info(f"Association established for time block {block_start} to {block_end}")

                # Create a DICOM Dataset for the query
                ds = pydicom.Dataset()
                ds.QueryRetrieveLevel = 'STUDY'
                ds.StudyDate = block_start.strftime('%Y%m%d')
                ds.AccessionNumber = ''
                ds.StudyInstanceUID = ''

                # Send the C-FIND query
                responses = assoc.send_c_find(ds, StudyRootQueryRetrieveInformationModelFind)

                # Process the responses
                for (status, identifier) in responses:
                    if status and status.Status in (0xFF00, 0xFF01) and identifier:
                        # Write the Accession Number and Study UID to the CSV file
                        writer.writerow([
                            identifier.get('AccessionNumber', ''),
                            identifier.get('StudyInstanceUID', '')
                        ])

                assoc.release()  # Release the association
                logging.info("Association released")

            else:
                logging.info("Association with PACS failed")

        current_date += timedelta(days=1)  # Move to the next day

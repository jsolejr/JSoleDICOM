import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import csv
import os
import pydicom
from pydicom.dataset import Dataset
from pynetdicom import AE, evt, QueryRetrievePresentationContexts
from pynetdicom.sop_class import StudyRootQueryRetrieveInformationModelFind


def load_config():
    config = {}
    try:
        with open("config.txt", "r") as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
    except Exception as e:
        print(f"Error loading config: {e}")
    return config

def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(title="Select the MRN list file")
    return file_path

def query_pacs(ae_title, ip, port, mrn):
    # Setup our application entity
    ae = AE()

    # Add the presentation contexts we're interested in
    #ae.supported_contexts = QueryRetrievePresentationContexts
    # Explicitly add the presentation context we need
    #ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
    ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)

    # Associate with the peer DICOM AE
    assoc = ae.associate(ip, port, ae_title=ae_title)

    if assoc.is_established:
        # Create our Identifier (query) dataset
        ds = Dataset()
        ds.PatientID = mrn
        ds.QueryRetrieveLevel = "STUDY"
        ds.StudyInstanceUID = ''
        ds.AccessionNumber = ''

        # Send the C-FIND request
        responses = assoc.send_c_find(ds, query_model='S')

        accession_numbers = []
        for (status, identifier) in responses:
            if status and 'Status' in status and status.Status == 0xFF00:
                accession_numbers.append(identifier.AccessionNumber)

        # Release the association
        assoc.release()
        return accession_numbers
    else:
        print("Association rejected, aborted or never connected")
        return []

def generate_csv(mrns, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['MRN', 'AccessionNumber'])
        for mrn, accession_numbers in mrns.items():
            for accession_number in accession_numbers:
                writer.writerow([mrn, accession_number])

if __name__ == "__main__":
    config = load_config()

    # Prompt user to select the MRN list file
    mrn_file_path = select_file()

    if mrn_file_path:
        mrns_with_accessions = {}
        with open(mrn_file_path, "r") as mrn_file:
            for mrn in mrn_file:
                mrn = mrn.strip()
                accession_numbers = query_pacs(config['Called_AE_Title_for_Source_PACS'], config['IP/Hostname_for_Source_PACS'], int(config['Port_for_Source_PACS']), mrn)
                mrns_with_accessions[mrn] = accession_numbers

        # Generate the CSV filename based on the current date and time
        date_str = datetime.now().strftime("%d%m%y")
        output_file = f"AccessionNumbers_{date_str}.csv"
        counter = 1
        while os.path.exists(output_file):
            output_file = f"AccessionNumbers_{date_str}_{counter}.csv"
            counter += 1

        generate_csv(mrns_with_accessions, output_file)
        print(f"Output saved to {output_file}")
    else:
        print("No file selected")

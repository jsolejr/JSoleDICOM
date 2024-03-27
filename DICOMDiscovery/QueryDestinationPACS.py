import tkinter as tk
from tkinter import filedialog
import csv
from datetime import datetime
import os
import pydicom
from pydicom.dataset import Dataset
from pynetdicom import AE, evt, QueryRetrievePresentationContexts

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
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select the CSV file with MRNs and Accession Numbers")
    return file_path

def query_pacs(ae_title, ip, port, accession_number):
    ae = AE()

    ae.supported_contexts = QueryRetrievePresentationContexts

    assoc = ae.associate(ip, int(port), ae_title=ae_title)

    if assoc.is_established:
        ds = Dataset()
        ds.AccessionNumber = accession_number
        ds.QueryRetrieveLevel = "STUDY"

        responses = assoc.send_c_find(ds, query_model='S')

        found = False
        for (status, identifier) in responses:
            if status and 'Status' in status and status.Status == 0xFF00:
                found = True
                break

        assoc.release()
        return found
    else:
        print("Association rejected, aborted or never connected")
        return False

def read_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [(row['MRN'], row['AccessionNumber']) for row in reader]

def generate_output(missing_accessions, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['AccessionNumber'])
        writer.writerows([[acc] for acc in missing_accessions])

if __name__ == "__main__":
    config = load_config()

    file_path = select_file()

    if file_path:
        records = read_csv(file_path)
        missing_accessions = []

        for _, accession_number in records:
            found = query_pacs(config['Called_AE_Title_for_Destination_PACS'], config['IP/Hostname_for_Destination_PACS'], config['Port_for_Destination_PACS'], accession_number)
            if not found:
                missing_accessions.append(accession_number)

        date_str = datetime.now().strftime("%d%m%y")
        output_file = f"MissingAccessions_{date_str}.csv"
        counter = 1
        while os.path.exists(output_file):
            output_file = f"MissingAccessions_{date_str}_{counter}.csv"
            counter += 1

        generate_output(missing_accessions, output_file)
        print(f"Missing accession numbers saved to {output_file}")
    else:
        print("No file selected")

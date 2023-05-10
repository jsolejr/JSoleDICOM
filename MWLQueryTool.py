import sys
from tkinter import simpledialog, Tk, messagebox
from pydicom.dataset import Dataset
from pynetdicom import AE, evt, build_role, debug_logger
from pynetdicom.sop_class import ModalityWorklistInformationFind

# Set up logging
debug_logger()

# Create a dialog box for user input
root = Tk()
root.withdraw()  # Hide the main window

calling_ae_title = simpledialog.askstring("Input", "Enter Calling AE Title:")
ae_title = simpledialog.askstring("Input", "Enter Destination AE Title:")
ip_address = simpledialog.askstring("Input", "Enter PACS Server IP:")
port = simpledialog.askinteger("Input", "Enter PACS Server Port:")

# Initialize the Application Entity (AE)
ae = AE(ae_title=calling_ae_title)
ae.add_requested_context(ModalityWorklistInformationFind)

# Create the query dataset
query = Dataset()
query.PatientName = ''
query.StudyDate = ''
query.Modality = 'CT'  # Set the modality you want to search for
query.AccessionNumber = ''
query.PatientID = ''
query.ScheduledProcedureStepDescription = ''

# Check if the user wants to provide query information
if messagebox.askyesno("Input", "Would you like to provide query information?"):
    query.PatientName = simpledialog.askstring("Input", "Enter Patient Name:")
    query.StudyDate = simpledialog.askstring(
        "Input", "Enter Study Date (YYYYMMDD):")
    query.Modality = simpledialog.askstring("Input", "Enter Modality:")
    query.AccessionNumber = simpledialog.askstring(
        "Input", "Enter Accession Number:")
    query.PatientID = simpledialog.askstring("Input", "Enter Patient ID:")
    query.ScheduledProcedureStepDescription = simpledialog.askstring(
        "Input", "Enter Scheduled Procedure Step Description:")

# Define the C-FIND request event handler


def handle_find(event):
    ds = event.identifier

    # Check if the response includes the Status element
    if 'Status' not in ds:
        return

    # Check the status of the C-FIND response
    status = ds.Status

    if status == 0xFF00:
        with open('output.txt', 'a') as f:
            f.write("Pending response received:\n")
            f.write(str(ds))
            f.write("\n\n")
        print("Pending response received:")
        print(ds)
    elif status in (0x0000, 0xFF00, 0xFF01):
        print("Success, C-FIND operation completed")
    else:
        print(f"Error, C-FIND operation failed with status: {status}")


# Associate the C-FIND event handler with the event
handlers = [(evt.EVT_C_FIND, handle_find)]

# Set up the remote PACS server information
assoc = ae.associate(ip_address, port, ae_title=ae_title, ext_neg=[
                     build_role(ModalityWorklistInformationFind)], evt_handlers=handlers)

if assoc.is_established:
    # Send the C-FIND request
    response = assoc.send_c_find(query, ModalityWorklistInformationFind)

    # Wait for the association to be released
    assoc.release()
else:
    error_msg = f"Failed to establish association with remote PACS server: {ip_address}:{port}"
    print(error_msg)
    messagebox.showerror("Error", error_msg)

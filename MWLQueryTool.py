from pynetdicom import AE
from pynetdicom.sop_class import ModalityWorklistInformationFind
import tkinter as tk
from tkinter import messagebox, simpledialog, Text, Scrollbar, Toplevel
import os
from pydicom.dataset import Dataset

# Create a simple GUI to prompt the user for inputs
root = tk.Tk()
root.withdraw()  # Hide the main window

# Prompt the user for the calling AE, called AE, remote IP and remote port
calling_ae = simpledialog.askstring("Input", "Please enter the calling AE:")
called_ae = simpledialog.askstring("Input", "Please enter the called AE:")
remote_ip = simpledialog.askstring("Input", "Please enter the remote IP:")
remote_port = simpledialog.askinteger("Input", "Please enter the remote port:")

# Create a dataset representing a worklist
dataset = Dataset()

# Prompt the user to modify the DICOM Query Attributes
dataset.PatientName = simpledialog.askstring("Input", "Please enter the Patient Name:")
dataset.StudyDate = simpledialog.askstring("Input", "Please enter the Study Date:")
dataset.Modality = simpledialog.askstring("Input", "Please enter the Modality:")
dataset.PatientID = simpledialog.askstring("Input", "Please enter the Patient ID:")

# Initialize the Application Entity and specify the SOP class
ae = AE(ae_title=calling_ae)
ae.add_requested_context(ModalityWorklistInformationFind)

# Establish the association
assoc = ae.associate(remote_ip, remote_port, ae_title=called_ae)

# Save the results in a list
results = []

# Send the C-FIND request
if assoc.is_established:
    responses = assoc.send_c_find(dataset, ModalityWorklistInformationFind)

    # Iterate over the responses
    for (status, identifier) in responses:
        if status:
            print("C-FIND response received with status", status)
            # Save the result
            results.append(identifier)

    # Release the association
    assoc.release()

# Create a new window to display the results
results_window = Toplevel(root)
results_window.title("Results")

# Create a scrollable text area
text_area = Text(results_window, wrap="word")
text_area.pack(side="left", fill="both", expand=True)
scrollbar = Scrollbar(results_window, command=text_area.yview)
scrollbar.pack(side="right", fill="y")
text_area['yscrollcommand'] = scrollbar.set

# Insert the results into the text area
for result in results:
    text_area.insert("end", str(result) + "\n")

# Show the window
results_window.mainloop()

from pynetdicom import AE
from pynetdicom.sop_class import ModalityWorklistInformationFind
import tkinter as tk
from tkinter import messagebox, simpledialog, Text, Scrollbar, Toplevel, filedialog
import os
from pydicom.dataset import Dataset
import logging
from pynetdicom import debug_logger
import csv

# Activate pynetdicom logging
debug_logger()

# Create a log file handler
handler = logging.FileHandler('dmwl_query.log')

# Get the logger used by pynetdicom (its name is 'pynetdicom')
logger = logging.getLogger('pynetdicom')

# Set the level of the logger and add the file handler
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Create a simple GUI to prompt the user for inputs
root = tk.Tk()
root.withdraw()  # Hide the main window

# Custom Dialog Class for user inputs
class InputDialog(simpledialog.Dialog):
    def body(self, master):
        labels = ["Called AE:", "Remote IP:", "Remote Port:", "Accession Number:",
                   "Patient Name:", "Patient ID:", "Modality:", "Scheduled Procedure Step Start Date:",
                   "Scheduled Procedure Step Start Time:", "Scheduled Procedure Step Description:"]
        self.entries = []

        for i, label in enumerate(labels):
            tk.Label(master, text=label).grid(row=i)
            entry = tk.Entry(master)
            entry.grid(row=i, column=1)
            self.entries.append(entry)

        return self.entries[0]  # initial focus

    def apply(self):
        self.result = tuple(entry.get() for entry in self.entries)


# Use dialog box to get user inputs
d = InputDialog(root)
(
    called_ae,
    remote_ip,
    remote_port,
    accession_number,
    patient_name,
    patient_id,
    modality,
    sps_start_date,
    sps_start_time,
    sps_description
) = d.result

# Ask the user to select a file containing a list of Calling AE titles and Modality codes
file_path = filedialog.askopenfilename()
if not file_path:
    messagebox.showerror("Error", "No file selected. Program will exit.")
    exit()

# Read the Calling AE titles and Modality codes from the CSV file
calling_ae_titles = []
modalities = []
try:
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:
                calling_ae_titles.append(row[0].strip())
                modalities.append(row[1].strip())
            else:
                messagebox.showwarning("Warning", f"Invalid row found in the file: {row}")
except Exception as e:
    messagebox.showerror("Error", f"Failed to read the file: {str(e)}")
    exit()

# Check if any Calling AE titles were found
if not calling_ae_titles:
    messagebox.showerror("Error", "No Calling AE titles found in the file. Program will exit.")
    exit()



# Remove leading/trailing whitespace and newline characters
calling_ae_titles = [title.strip() for title in calling_ae_titles]

# Create a dataset representing a worklist
dataset = Dataset()
dataset.PatientName = patient_name
dataset.AccessionNumber = accession_number
dataset.PatientID = patient_id

# Create a dataset for the ScheduledProcedureStepSequence
scheduled_procedure_step_sequence = Dataset()
scheduled_procedure_step_sequence.Modality = modality
scheduled_procedure_step_sequence.ScheduledProcedureStepStartDate = sps_start_date
scheduled_procedure_step_sequence.ScheduledProcedureStepStartTime = sps_start_time
scheduled_procedure_step_sequence.ScheduledProcedureStepDescription = sps_description

# Add the ScheduledProcedureStepSequence to the main dataset
dataset.ScheduledProcedureStepSequence = [scheduled_procedure_step_sequence]

# Initialize the Application Entity and specify the SOP class
ae = AE()
ae.add_requested_context(ModalityWorklistInformationFind)

# Save the results in a list
all_results = []

# Perform DMWL Query for each Calling AE title and Modality code
for calling_ae, modality in zip(calling_ae_titles, modalities):
    ae.ae_title = calling_ae
    scheduled_procedure_step_sequence.Modality = modality

    # Establish the association
    assoc = ae.associate(remote_ip, int(remote_port), ae_title=called_ae)

    # Send the C-FIND request
    if assoc.is_established:
        try:
            responses = assoc.send_c_find(
                dataset=dataset,  # Specify the dataset parameter with the query dataset
                query_model=ModalityWorklistInformationFind
            )

            # Save the results for this Calling AE title in a list
            results = []

            # Iterate over the responses
            for (status, identifier) in responses:
                if status:
                    print("C-FIND response received with status", status)
                    # Save the result
                    if identifier is not None:  # Check if identifier is not None
                        results.append(identifier)

            # Release the association
            assoc.release()

            # Add the results for this Calling AE title to the overall results list
            all_results.append((calling_ae, results))
        except:
            print("Exception occurred during handling of responses")
            assoc.abort()
    else:
        print("Association rejected for Calling AE:", calling_ae)

# Create a new window to display the results
results_window = Toplevel(root)
results_window.title("Results")

# Create a scrollable text area
text_area = Text(results_window, wrap="word")
text_area.pack(side="left", fill="both", expand=True)
scrollbar = Scrollbar(results_window, command=text_area.yview)
scrollbar.pack(side="right", fill="y")
text_area['yscrollcommand'] = scrollbar.set

# Format and insert the results into the text area to include a running count
for idx, (calling_ae, results) in enumerate(all_results):
    text_area.insert("end", f"---- Calling AE: {calling_ae} ----\n")
    count = 0  # Initialize the result count for each Calling AE title
    for result in results:
        count += 1  # Increment the result count
        text_area.insert("end", f"----- Result {count} -----\n")

        # Access ScheduledProcedureStepSequence with fallback to "N/A" if not present
        if result is not None:  # Check if result is not None
            scheduled_procedure_step_seq = result.get("ScheduledProcedureStepSequence", "N/A")

            if scheduled_procedure_step_seq != "N/A":
                for scheduled_procedure_step in scheduled_procedure_step_seq:
                    start_date = scheduled_procedure_step.get("ScheduledProcedureStepStartDate", "N/A")
                    start_time = scheduled_procedure_step.get("ScheduledProcedureStepStartTime", "N/A")
                    description = scheduled_procedure_step.get("ScheduledProcedureStepDescription", "N/A")
                    text_area.insert("end", f"ScheduledProcedureStepStartDate: {start_date}\n")
                    text_area.insert("end", f"ScheduledProcedureStepStartTime: {start_time}\n")
                    text_area.insert("end", f"ScheduledProcedureStepDescription: {description}\n")

            for tag, value in result.items():
                if tag == "00080060" or tag == "00400100":  # Skip Modality and ScheduledProcedureStepSequence attribute
                    continue
                text_area.insert("end", f"{tag}: {value}\n")

        text_area.insert("end", "\n")

# Define a function to save the results to a file
def save_results():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv")
    if file_path:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Calling AE", "Result", "Specific Character Set", "Accession Number", "Patient's Name", "Patient ID", "Modality", "Scheduled Procedure Step Start Date", "Scheduled Procedure Step Start Time", "Scheduled Procedure Step Description"])
            for idx, (calling_ae, results) in enumerate(all_results):
                for i, result in enumerate(results):
                    sps_sequence = result.get("ScheduledProcedureStepSequence", "N/A")
                    if sps_sequence != "N/A":
                        for sps in sps_sequence:
                            modality = sps.get("Modality", "N/A")
                            start_date = sps.get("ScheduledProcedureStepStartDate", "N/A")
                            start_time = sps.get("ScheduledProcedureStepStartTime", "N/A")
                            description = sps.get("ScheduledProcedureStepDescription", "N/A")
                            writer.writerow([calling_ae, i+1, result.get("SpecificCharacterSet", "N/A"), result.get("AccessionNumber", "N/A"), result.get("PatientName", "N/A"), result.get("PatientID", "N/A"), modality, start_date, start_time, description])
        messagebox.showinfo("Save Results", "Results saved successfully.")

# Create a "Save Results" button
save_button = tk.Button(results_window, text="Save Results", command=save_results)
save_button.pack()


# Define a close function to destroy both the result and root windows
def close_all():
    results_window.destroy()
    root.destroy()

# Bind the close function to the close button
results_window.protocol('WM_DELETE_WINDOW', close_all)

# Show the window
results_window.mainloop()

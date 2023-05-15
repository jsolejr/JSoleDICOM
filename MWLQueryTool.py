from pynetdicom import AE
from pynetdicom.sop_class import ModalityWorklistInformationFind
import tkinter as tk
from tkinter import messagebox, simpledialog, Text, Scrollbar, Toplevel, filedialog
import os
from pydicom.dataset import Dataset

# Create a simple GUI to prompt the user for inputs
root = tk.Tk()
root.withdraw()  # Hide the main window

# Custom Dialog Class for user inputs
class InputDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Calling AE:").grid(row=0)
        tk.Label(master, text="Called AE:").grid(row=1)
        tk.Label(master, text="Remote IP:").grid(row=2)
        tk.Label(master, text="Remote Port:").grid(row=3)
        tk.Label(master, text="Patient Name:").grid(row=4)
        tk.Label(master, text="Study Date:").grid(row=5)
        tk.Label(master, text="Modality:").grid(row=6)
        tk.Label(master, text="Patient ID:").grid(row=7)

        self.e1 = tk.Entry(master)
        self.e2 = tk.Entry(master)
        self.e3 = tk.Entry(master)
        self.e4 = tk.Entry(master)
        self.e5 = tk.Entry(master)
        self.e6 = tk.Entry(master)
        self.e7 = tk.Entry(master)
        self.e8 = tk.Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)
        self.e5.grid(row=4, column=1)
        self.e6.grid(row=5, column=1)
        self.e7.grid(row=6, column=1)
        self.e8.grid(row=7, column=1)

        return self.e1  # initial focus

    def apply(self):
        self.result = (self.e1.get(), self.e2.get(), self.e3.get(), self.e4.get(), self.e5.get(), self.e6.get(), self.e7.get(), self.e8.get())

# Use dialog box to get user inputs
d = InputDialog(root)
calling_ae, called_ae, remote_ip, remote_port, patient_name, study_date, modality, patient_id = d.result

# Create a dataset representing a worklist
dataset = Dataset()
dataset.PatientName = patient_name
dataset.StudyDate = study_date
dataset.Modality = modality
dataset.PatientID = patient_id

# Initialize the Application Entity and specify the SOP class
ae = AE(ae_title=calling_ae)
ae.add_requested_context(ModalityWorklistInformationFind)

# Establish the association
assoc = ae.associate(remote_ip, int(remote_port), ae_title=called_ae)

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

# Define a function to save the results to a file
def save_results():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        with open(file_path, 'w') as file:
            for result in results:
                file.write(str(result) + "\n")
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

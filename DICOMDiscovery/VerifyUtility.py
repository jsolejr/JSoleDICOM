import tkinter as tk
from tkinter import messagebox
import subprocess

def run_query_source_pacs():
    try:
        subprocess.run(["python", "QuerySourcePACS.py"], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run QuerySourcePACS.py: {e}")

def run_query_destination_pacs():
    try:
        subprocess.run(["python", "QueryDestinationPACS.py"], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run QueryDestinationPACS.py: {e}")

def run_configuration():
    try:
        subprocess.run(["python", "configuration.py"], check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run configuration.py: {e}")

def close_program():
    root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PACS Utility")
    root.geometry("400x200")  # Set the size of the dialog box here (width x height)


    tk.Button(root, text='Read Source PACS', command=run_query_source_pacs).pack(fill=tk.X, padx=5, pady=5)
    tk.Button(root, text='Read Destination PACS', command=run_query_destination_pacs).pack(fill=tk.X, padx=5, pady=5)
    tk.Button(root, text='Configuration', command=run_configuration).pack(fill=tk.X, padx=5, pady=5)
    tk.Button(root, text='Close', command=close_program).pack(fill=tk.X, padx=5, pady=5)

    root.mainloop()

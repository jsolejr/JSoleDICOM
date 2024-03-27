import tkinter as tk
from tkinter import messagebox
import subprocess

def load_existing_config():
    config = {}
    try:
        with open("config.txt", "r") as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
    except FileNotFoundError:
        print("Config file not found. Proceeding with empty fields.")
    except Exception as e:
        print(f"Error reading config file: {e}")
    return config

class ConfigDialog:
    def __init__(self, root, existing_config):
        self.root = root
        self.fields = [
            "Calling AE Title", "Called AE Title for Source PACS",
            "IP/Hostname for Source PACS", "Port for Source PACS",
            "Called AE Title for Destination PACS", "IP/Hostname for Destination PACS",
            "Port for Destination PACS"
        ]
        self.entries = {}
        self.existing_config = existing_config

    def show(self):
        for field in self.fields:
            underscore_field = field.replace(' ', '_')
            row = tk.Frame(self.root)
            label = tk.Label(row, width=30, text=field, anchor='w')
            entry = tk.Entry(row)
            entry.insert(0, self.existing_config.get(underscore_field, ''))  # Pre-fill with existing config if available
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.entries[underscore_field] = entry

    def save_config(self):
        try:
            with open("config.txt", "w") as file:
                for key, entry in self.entries.items():
                    file.write(f"{key}={entry.get()}\n")
            messagebox.showinfo("Info", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def close_dialog(self):
        self.root.destroy()

    def test_connection(self):
        # Assuming connectivitytest.py is in the same directory and executable
        subprocess.run(["python", "connectivitytest.py"], check=True)

if __name__ == "__main__":
    existing_config = load_existing_config()
    root = tk.Tk()
    root.title("PACS Configuration")
    app = ConfigDialog(root, existing_config)
    app.show()
    tk.Button(root, text='Save Configuration', command=app.save_config).pack(side=tk.RIGHT, padx=5, pady=5)
    tk.Button(root, text='Test', command=app.test_connection).pack(side=tk.RIGHT, padx=5, pady=5)
    tk.Button(root, text='Close', command=app.close_dialog).pack(side=tk.RIGHT, padx=5, pady=5)
    root.mainloop()

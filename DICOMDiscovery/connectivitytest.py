# ConnectivityTest.py
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import logging
from pynetdicom import AE
from pynetdicom.sop_class import VerificationSOPClass
import sys

print(sys.executable)

# Configure logging for the script
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    config = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.txt')

    try:
        with open(config_path, "r") as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        messagebox.showerror("Error", "Configuration file not found.")
        return None
    except Exception as e:
        logging.error(f"An error occurred reading config: {e}")
        messagebox.showerror("Error", str(e))
        return None

    return config

def test_ping(ip_address):
    # Ping the provided IP address.
    try:
        response = subprocess.run(["ping", "-n" if os.name == 'nt' else "-c", "4", ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ping_result = response.stdout + "\n" + response.stderr
        logging.info(f"Ping result for {ip_address}:\n{ping_result}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Ping failed for {ip_address}: {e}")
        ping_result = f"Ping failed for {ip_address}: {e}"
    return ping_result

def dicom_echo(config):
    ae = AE(ae_title=config.get('Calling_AE_Title', 'PYNETDICOM'))
    ae.add_requested_context(VerificationSOPClass)

    assoc = ae.associate(config.get('IP_Hostname_for_Source_PACS', ''),
                         int(config.get('Port_for_Source_PACS', '0')),
                         ae_title=config.get('Called_AE_Title_for_Source_PACS', 'ANY-SCP'))
    if assoc.is_established:
        status = assoc.send_c_echo()
        assoc.release()
        return "DICOM Echo Succeeded" if status and status.Status == 0x0000 else "DICOM Echo Failed"
    else:
        return "DICOM Echo Failed: Association not established"

def test_source_pacs():
    config = load_config()
    if config:
        source_pacs_ip = config.get('IP/Hostname_for_Source_PACS')
        ping_result = test_ping(source_pacs_ip)
        messagebox.showinfo("Ping Source PACS", f"Ping Result:\n{ping_result}")
        echo_result = dicom_echo(config)
        messagebox.showinfo("Test Source PACS", f"DICOM Echo Result:\n{echo_result}")

def test_destination_pacs():
    config = load_config()
    if config:
        destination_pacs_ip = config.get('IP/Hostname_for_Destination_PACS')
        ping_result = test_ping(destination_pacs_ip)
        messagebox.showinfo("Ping Destination PACS", f"Ping Result:\n{ping_result}")
        echo_result = dicom_echo(config)
        messagebox.showinfo("Test Destination PACS", f"DICOM Echo Result:\n{echo_result}")

def close_application():
    root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PACS Connectivity Test")
    root.geometry("400x200")  # Set the size of the dialog box here (width x height)

    # Test Source PACS button
    tk.Button(root, text="Test Source PACS", command=test_source_pacs).pack(fill=tk.X, padx=10, pady=5)

    # Test Destination PACS button
    tk.Button(root, text="Test Destination PACS", command=test_destination_pacs).pack(fill=tk.X, padx=10, pady=5)

    # Close button
    tk.Button(root, text="Close", command=close_application).pack(fill=tk.X, padx=10, pady=5)

    root.mainloop()

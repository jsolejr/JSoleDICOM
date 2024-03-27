# ConnectivityTest.py
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import logging
from pynetdicom import AE, VerificationPresentationContexts, debug_logger

# Uncomment the following line if you wish to enable logging for pynetdicom
# debug_logger()

# Configure logging for the script
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    config = {
        'Calling_AE_Title': '',
        'Called_AE_Title_for_Source_PACS': '',
        'IP_Hostname_for_Source_PACS': '',
        'Port_for_Source_PACS': '',
        'Called_AE_Title_for_Destination_PACS': '',
        'IP_Hostname_for_Destination_PACS': '',
        'Port_for_Destination_PACS': ''
    }
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.txt')

    try:
        with open(config_path, "r") as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        key, value = parts
                        key = key.replace('/', '_').strip()
                        config[key] = value.strip()
                        logging.debug(f"Loaded {key}: {value}")
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        messagebox.showerror("Error", "Configuration file not found.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", str(e))

    return config

def ping(host):
    count_flag = '-n' if os.name == 'nt' else '-c'
    count = '4'
    try:
        logging.debug(f"Executing ping on host: {host}")
        response = subprocess.run(["ping", count_flag, count, host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(f"Ping response: {response.stdout}")
        if response.stderr:
            logging.error(f"Ping error: {response.stderr}")
        return response.stdout + "\n" + response.stderr
    except subprocess.CalledProcessError as e:
        logging.error(f"Ping failed: {e}")
        return f"Ping failed: {e}"

def dicom_echo(aet, host, port):
    ae = AE(aetitle=aet)
    ae.supported_contexts = VerificationPresentationContexts

    try:
        assoc = ae.associate(host, int(port))
        if assoc.is_established:
            status = assoc.send_c_echo()
            assoc.release()
            if status:
                if status.Status in range(0x0000, 0x0100):
                    return "DICOM Echo Succeeded"
                else:
                    return f"DICOM Echo Failed with status: {status.Status}"
            else:
                return "DICOM Echo Failed: No response received"
        else:
            return "DICOM Echo Failed: Association not established"
    except Exception as e:
        return f"DICOM Echo Failed: {e}"

def test_source_pacs():
    messagebox.showinfo("Running Tests", "The tests are now running. Please wait...")
    config = load_config()
    if config:
        ping_result = ping(config["IP_Hostname_for_Source_PACS"])
        echo_result = dicom_echo(config["Calling_AE_Title"], config["IP_Hostname_for_Source_PACS"], config["Port_for_Source_PACS"])
        messagebox.showinfo("Test Source PACS", f"Ping Result:\n{ping_result}\n\nDICOM Echo Result:\n{echo_result}")

def test_destination_pacs():
    messagebox.showinfo("Running Tests", "The tests are now running. Please wait...")
    config = load_config()
    if config:
        ping_result = ping(config["IP_Hostname_for_Destination_PACS"])
        echo_result = dicom_echo(config["Calling_AE_Title"], config["IP_Hostname_for_Destination_PACS"], config["Port_for_Destination_PACS"])
        messagebox.showinfo("Test Destination PACS", f"Ping Result:\n{ping_result}\n\nDICOM Echo Result:\n{echo_result}")

def close_application():
    root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PACS Connectivity Test")

    # Test Source PACS button
    tk.Button(root, text="Test Source PACS", command=test_source_pacs).pack(fill=tk.X, padx=10, pady=5)

    # Test Destination PACS button
    tk.Button(root, text="Test Destination PACS", command=test_destination_pacs).pack(fill=tk.X, padx=10, pady=5)

    # Close button
    tk.Button(root, text="Close", command=close_application).pack(fill=tk.X, padx=10, pady=5)

    root.mainloop()

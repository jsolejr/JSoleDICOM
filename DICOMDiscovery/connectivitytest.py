# ConnectivityTest.py
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import logging

# Configure logging
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
    
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
    config_path = os.path.join(script_dir, 'config.txt')  # Path to the config file

    try:
        with open(config_path, "r") as file:
            for line in file:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    key, value = parts
                    # Replace slash with underscore for consistency with the script's config dictionary
                    key = key.replace('/', '_')
                    config[key.strip()] = value.strip()
                    logging.debug(f"Loaded {key}: {value}")
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        messagebox.showerror("Error", "Configuration file not found.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", str(e))

    return config


# Function to perform a ping test
def ping(host):
    count_flag = '-n' if os.name == 'nt' else '-c'
    count = '4'
    try:
        logging.debug(f"Executing ping on host: {host}")
        response = subprocess.run(["ping", count_flag, count, host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.debug(f"Ping response: {response.stdout}")
        logging.error(f"Ping error: {response.stderr}")
        return response.stdout + "\n" + response.stderr
    except subprocess.CalledProcessError as e:
        logging.error(f"Ping failed: {e}")
        return f"Ping failed: {e}"


# Function to perform a DICOM Echo (C-ECHO) test using the echoscu command from DCMTK tools
def dicom_echo(aet, host, port):
    # Construct the path to echoscu executable relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    echoscu_path = os.path.join(script_dir, 'DCMTK', 'echoscu')
    if os.name == 'nt':
        echoscu_path += '.exe'

    try:
        echo_response = subprocess.run([echoscu_path, "-aec", aet, host, port], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if echo_response.returncode == 0:
            return "DICOM Echo Succeeded"
        else:
            return f"DICOM Echo Failed: {echo_response.stderr}"
    except FileNotFoundError:
        return f"echoscu command not found at {echoscu_path}. Please check the path to DCMTK."


# Function to load configuration from the config.txt file
def load_config():
    config = {
        'Calling_AE_Title': '',
        'Called_AE_Title_for_Source_PACS': '',
        'IP_Hostname_for_Source_PACS': '',
        'Port_for_Source_PACS': '',
        'Called_AE_Title_for_Destination_PACS': '',
        'IP_Hostname_for_Destination_PACS': '',
        'Port_for_Destination_PACS': ''
        # Add default values for other expected configuration keys if needed.
    }
    
    # Print default config values (this should be indented to be part of the load_config function but not part of the for loop)
    for key, value in config.items():
        print(f"{key}: {value}")

    script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
    config_path = os.path.join(script_dir, 'config.txt')  # Path to the config file

    try:
        with open(config_path, "r") as file:
            for line in file:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    key, value = parts
                    config[key] = value
    except FileNotFoundError:
        messagebox.showerror("Error", "Configuration file not found.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

    return config

# Function to test source PACS
def test_source_pacs():
    messagebox.showinfo("Running Tests", "The tests are now running. Please wait...")
    config = load_config()
    if config:
        ping_result = ping(config["IP_Hostname_for_Source_PACS"])
        echo_result = dicom_echo(config["Calling_AE_Title"], config["IP_Hostname_for_Source_PACS"], config["Port_for_Source_PACS"])
        messagebox.showinfo("Test Source PACS", f"Ping Result:\n{ping_result}\n\nDICOM Echo Result:\n{echo_result}")

# Function to test destination PACS
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

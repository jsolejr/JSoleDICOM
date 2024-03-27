# 🌟 JSoleDICOM - DICOM Tools Repository 🌟

This repository contains a collection of Python-based DICOM tools to perform various tests and operations on DICOM functionality. These tools are designed to help users interact with PACS servers, DICOM images, and other DICOM-related tasks.

## 🚀 Features

- ✅ Query DICOM Modality Worklist (MWL) from a PACS server using C-FIND operation. - In Progress
- ✅ Simple Study Count (`SimpleStudyCount.py`)
- This tool performs a simple DICOM query to retrieve study accession numbers and their corresponding Study Instance UIDs from a PACS server. The results are logged into a CSV file, providing a straightforward way to compile a list of studies within a specified date range.
- ✅ Discovery Tool (`discovery_tool.py`)
This tool allws to perform various queries against a pacs and return results in various outputs.  The current code returns exams that are missing study descriptions.

For detailed usage, see [Simple Study Count README](SimpleStudyCountREADME.md).
- ❓ Transfer DICOM images to and from PACS servers using C-STORE and C-GET/C-MOVE operations. - TBD
- ❓ Parse and display DICOM image headers and metadata. - TBD
- ❓ Modify DICOM image headers and save them to new files. -TBD
- ❓ Perform image processing and analysis on DICOM images. -TBD
- ❓ Perform a discovery on a PACS. - In Progress

## 📦 Requirements

- Python 3.6+
- pynetdicom: `pip install pynetdicom`
- pydicom: `pip install pydicom`
- tkinter: usually comes pre-installed with Python, but if it's missing, you can install it using your package manager, e.g., `apt-get install python3-tk` for Debian-based systems or `pacman -S tk` for Arch-based systems.

## 🛠️ Tools

1. **[📊 DICOM Modality Worklist Query Tool (MWLQueryTool.py)](MWLQuerryToolREADME.md):** Query a DICOM Modality Worklist (MWL) from a PACS server using the C-FIND operation.
2. **[📊 Simple Study Count (SimpleStudyCount.py)](SimpleStudyCountREADME.md):** Perform a simple query to retrieve study accession numbers and corresponding Study Instance UIDs from a PACS server, logging the results to a CSV file.
3. **[📊 Discovery Tool (discovery_tool.py)](discovery_toolReadme.md):** Perform various queries against a pacs and return results in various outputs.
4. 📝 _More tools will be added in the future._


## 🎯 Usage

Each tool in this repository can be used independently. Follow the instructions provided in the individual README files for each tool to set up the required dependencies and run the tool.

## 🤝 Contributing

We welcome contributions to improve and expand the capabilities of these DICOM tools. If you would like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes and commit them to your branch.
4. Create a pull request, describing the changes you made and the problem they address.

Please ensure your code follows the existing style and structure of the repository.

## 📄 License

This project is licensed under the terms of the MIT license.

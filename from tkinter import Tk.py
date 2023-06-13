from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Open file dialog to select the input file
Tk().withdraw()
input_file = askopenfilename(title="Select Input File")

# Read the values from the input file
with open(input_file, 'r') as file:
    items = file.read().splitlines()

# Remove all characters except the first two characters from each item
modified_items = [item[:2] for item in items]

# Display the modified items
for item in modified_items:
    print(item)

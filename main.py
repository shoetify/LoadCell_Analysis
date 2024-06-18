import os
from Util import LoadCell_Util

# Read all the table in the log file
hasMD = False
tables = []
for file in os.listdir():
    if file.endswith('.md'):
        hasMD = True
        tables = tables + LoadCell_Util.parse_markdown(file)

# If no log file, then need to input the log manually.
if not hasMD:
    raise TypeError("Cannot find any log in this folder!!!")

columns = LoadCell_Util.read_txt_file("Full Scale.txt")
print(len(columns[0]))
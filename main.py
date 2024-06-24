import os
import yaml
from Util import LoadCell_Util

# Read all the table in the log file
hasMD = False
tables = []
for file in os.listdir():
    if file.endswith('.md'):
        hasMD = True
        print('Reading file [' + file + '] ...')
        tables = tables + LoadCell_Util.parse_markdown(file)



# If no log file, then need to input the log manually.
if not hasMD:
    raise TypeError("Cannot find any log in this folder!!!")

# Read the config file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Get Wind speed relationship
wind_speed_a, wind_speed_b = LoadCell_Util.extract_numbers_from_string(config['Parameter']['WindSpeed_relationship'])

stable_time_0Hz = config['Parameter']['Stable_time_0Hz']
stable_time_others = config['Parameter']['Stable_time_others']
gap_before_next_wind_speed = config['Parameter']['Gap_before_next_wind_speed']


# for table in tables:
#     print(table)
#
# columns = LoadCell_Util.read_txt_file("Full Scale.txt")
# print(len(columns[0]))

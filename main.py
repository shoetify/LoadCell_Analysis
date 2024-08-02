import os
import yaml
from Util import LoadCell_Util
from DataAnalysis import DataAnalyzer

# Read all the tables in the log file
hasMD = False
tables = []
for file in os.listdir():
    if file.endswith('.md'):
        hasMD = True
        print(f'Reading file [{file}] ...')
        tables += LoadCell_Util.parse_markdown(file)
        print(f'Successfully read file [{file}] ...')

# If no log file, then need to input the log manually.
if not hasMD:
    raise TypeError("Cannot find any log in this folder!!!")
print('Lab log reading finish ...')

print('Config file reading ... ')
# Read the config file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
print('Config file reading successfully ...')

# Get Wind speed relationship
wind_speed_a, wind_speed_b = LoadCell_Util.extract_numbers_from_string(config['Parameter']['WindSpeed_relationship'])

# Change the raw log table into proceeded table and ready for calculation
stable_time_0Hz = config['Parameter']['Stable_time_0Hz']
stable_time_others = config['Parameter']['Stable_time_others']
gap_before_next_wind_speed = config['Parameter']['Gap_before_next_wind_speed']
proceeded_tables = LoadCell_Util.proceed_table(tables, stable_time_0Hz, stable_time_others, gap_before_next_wind_speed,
                                               wind_speed_a, wind_speed_b)

print(" ")

# Start analyzing the data
sample_rate = config['Parameter']['Sample_rate']
mean_tables, rms_tables = DataAnalyzer.analyze(proceeded_tables, sample_rate, stable_time_others, stable_time_0Hz)

LoadCell_Util.toExcel(proceeded_tables, mean_tables, rms_tables)

# Input
Needs three types of files:
## 1. Raw data of Load cell
- a .txt file.

- 12 columns of data (2 Load cell works in the same time, each load cell have 6 channels) 

## 2. Log data for experiment 
example log data:

![image](https://github.com/user-attachments/assets/7c6b0972-695f-4132-a9fd-1a6565bb704c)

- a .xlsx file name end with "log.xlsx".

- 1st column is the motor's speed (will translate to wind speed during the calculation).

- 2nd column is start time of the test section.

- 3rd column is end time of the test section. if next test start immediately(next start time = this end time), you can leave this cell blank.

- 4th column is the raw data file name. You can leave this cell blank if this test is at the same raw data file with the last one.

## 3. Config file
Change the parameter in the config file

### Data_reading:
This section is the parameter related to data reading.

- WindSpeed_relationship: 

  This relationship translate the speed of motor into the wind speed. If the speed of motor is 0Hz, the wind speed will set to 0m/s.

- Sample_rate: unit(Hz)

  The recording sample rate of the load cell. This parameter is to translate the raw data into real time.

- Stable_time_0Hz: unit(s)

  The following three parameter is to deside the stable time after and before the wind speed is change.

  This parameter is to deside how many second of data were not used when the wind speed change(it start from 0Hz). Normally it will be larger as it takes more time to stable when it start from 0m/s.

- Stable_time_others: unit(s)

  This parameter is to deside how many second of data were not used when the wind speed change(not start from 0Hz).

- Gap_before_next_wind_speed: unit(s)

  This parameter is to deside how many second of data were not used before the wind speed change. Recommend to set as 1 to avoid mistake during the experiment (change the wind speed early).

### Data_calculation:
This section is the parameter related to the drag and lift coefficient calculating.

- air_density: unit(kg/m3)

- cylinder_diameter: unit(m)

- test_section_length: unit(m)

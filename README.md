# 1. Background information

This small program is used to solve the problem of:

## 1.1 Problem identify

- Load cells were used to collect the hydrodynamic forces in lab.
- When these hydrodynamic forces is vibrating, the load cell's reading will offset gradually.

    For example: in the following signal of time - drag force in constant wind speed, if we used 2 degree polynomial fit the signal, we can see the mean drag force is keep decreasing.
![image](https://github.com/user-attachments/assets/7a0139c6-d2c0-491b-8d8e-586f61dcc338)

  
- The largest offset rate we recorded is around $10^{-6} N/ms$, sometimg increase and sometime decrease, which means for a 20 minutes experiment, there will be: $10^{-6}\*1000\*20\*60=1.2N$ error.
- 1.2N error per load cell. Compare to the total drag force normally $2-4N$, this error is not acceptable.

![image](https://github.com/user-attachments/assets/3030c313-6320-4061-a8f5-4932a1644a4d)




# 2. Input
Needs three types of files:
## 2.1. Raw data of Load cell

It's normally a:
- ".txt" file.

- 12 columns of data inside the file (2 Load cell works in the same time, each load cell have 6 channels) 

## 2.2. Log data for experiment 
example log data:

![image](https://github.com/user-attachments/assets/7c6b0972-695f-4132-a9fd-1a6565bb704c)

- All the files in the folder will be scanned and all files whose name end with "log.xlsx" will be consided as log data. For example: "test log.xlsx"

- 1st column is the motor's speed (will translate to wind speed during the calculation).

- 2nd column is start time of the test section.

- 3rd column is end time of the test section. if next test start immediately(i.e. next start time = this end time), you can leave this cell blank.

- 4th column is the raw data file name (i.e. file name of section 1). You can leave this cell blank if this test section and last test section's data are in the same raw data file.

## 2.3. Config file
Contain all the parameters need during the calculation

### 2.3.1. Data_reading:
This section is the parameter related to data reading.

- WindSpeed_relationship: 

  This relationship translate the speed of motor into the wind speed. 
  
  If the speed of motor is 0Hz, the wind speed will set to 0m/s automatically.

  If your input is wind speed directly, you can input: y = x


- Sample_rate: unit(Hz)

  The recording sample rate of the load cell.


The following three parameter is to deside the stable time after and before the wind speed is change.

- Stable_time_0Hz: unit(s)

  This parameter is to deside how many second of data were not used when the wind speed change from 0m/s. Normally it will be larger as it takes more time to stable when it starts from 0m/s.


- Stable_time_others: unit(s)

  This parameter is to deside how many second of data were not used when the wind speed change not from 0m/s.

  Recommend to set as 10.


- Gap_before_next_wind_speed: unit(s)

  This parameter is to deside how many second of data were not used before the wind speed change. 

  Recommend to set as 1 to avoid mistake during the experiment (change the wind speed early).

### 2.3.2. Data_calculation:
This section is the parameter related to the drag and lift coefficient calculating.

- air_density: unit(kg/m3)

- cylinder_diameter: unit(m)

- test_section_length: unit(m)

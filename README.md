# 1. Background information

This small program is used to solve the problem of:

## 1.1 Problem identify

- Load cells were used to collect the hydrodynamic forces in lab.
- When these hydrodynamic forces is vibrating, the load cell's reading will offset gradually.

    For example: in the following signal of time - drag force in constant wind speed, if we used 2 degree polynomial fit the signal, we can see the mean drag force is keep decreasing.
![image](https://github.com/user-attachments/assets/7a0139c6-d2c0-491b-8d8e-586f61dcc338)

  
- The largest offset rate we recorded is around $10^{-6} N/ms$, sometimg increase and sometime decrease, which means for a 20 minutes experiment, there will be: $10^{-6}\*1000\*20\*60=1.2N$ error.
- 1.2N error per load cell. Compare to the total drag force normally $2-4N$, this error is not acceptable.

## 1.2 Solution procedure

We take the part of our sample test data as an example, shown in the following figure. This is part of the drag force data
in one of our experiment. The wind speed started at $0m/s$ at 0s, then increased to $2.52m/s$ at 60s ($0.6*10^{-5}ms$).
After that, the wind speed increased to $3.38m/s$ at 180s and $4.25m/s$ at 300s. The load cell kept recording the drag 
force data during this procedure.
![image](https://github.com/user-attachments/assets/3030c313-6320-4061-a8f5-4932a1644a4d)

Here's our solution procedure:
- (1) Calculate the stable range of data.
  
  Normally it take few seconds to let the wind speed and reading stable after the wind speed been adjusted (Usually 30 
seconds for wind speed start from $0m/s$ and 10 seconds for other conditions). In addition, the last 1 second of each 
section of data is not considered to prevent the recording error. 

  So in this case, we take $0-59s$ as the first section, $90-179s$ as the second section, $190-299s$ as the third section
of stable range.

  **Note: the parameter of stable range calculation can be customized at config.yaml**

- (2) Do linear polynomial fit for each range. We can get three equation: 
  
  $y_1=a_1x+b_1$

  $y_2=a_2x+b_2$

  $y_3=a_3x+b_3$

- (3) For the first range, we only need to deduct the first range's error to each point.
  
  i.e. $F_ireal=F_i-a_1*i$, $0<i<0.6*10^5$

- (4) For the other range, we need to deduct both that range's error and error accumulated by previous ranges.
  
  i.e. For $2_{nd}$ range, $F_ireal = F_i-a_2\*(i-0.6\*10^5)-a_1\*0.6\*10^5$, $0.6*10^5<i<1.8*10^5$
  
  For $3^{rd}$ range, $F_ireal = F_i-a_3\*(i-1.8\*10^5)-a_1\*0.6\*10^5-a_2*(1.8-0.6)*10^5$, $1.8*10^5<i<3.0*10^5$
  
  **Note: Here we use the polynomial fit result in the stable range to represent the whole test range, because it's hard
to calculate the error during the wind speed change**

- (5) After processing the data by step(1)-(4), we can use these data for force calculation.



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

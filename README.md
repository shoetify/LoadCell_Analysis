# 📘 Load Cell Drift Correction for Hydrodynamic Force Measurement

## 1. Overview

This tool corrects for systematic drift observed in load cell readings during hydrodynamic experiments in wind tunnels.

---

## 2. Background

### 2.1 Problem Statement

- Load cells are used in laboratory setups to measure hydrodynamic forces.
- When subjected to vibration, load cells often exhibit a **gradual drift** in their baseline readings.

📉 **Example**:  
In the figure below, a constant-wind-speed drag force signal shows a downward trend when fitted with a second-order polynomial, indicating baseline drift:

![Example Drift](https://github.com/user-attachments/assets/7a0139c6-d2c0-491b-8d8e-586f61dcc338)

- The **maximum recorded drift rate** is approximately `10⁻⁶ N/ms`, which translates to a **1.2 N error over 20 minutes** — an unacceptable deviation considering that typical drag forces are only 2–4 N.

---


### 2.2 Solution Approach

We demonstrate the correction method using a sample dataset. The experiment follows these phases:

| Time (s) | Wind Speed (m/s) |
|----------|------------------|
| 0        | 0                |
| 60       | 2.52             |
| 180      | 3.38             |
| 300      | 4.25             |

![Test Signal](https://github.com/user-attachments/assets/3030c313-6320-4061-a8f5-4932a1644a4d)

#### Correction Steps:

1. **Define stable data ranges**:  
   - Allow ~30 seconds for initial stabilization and ~10 seconds after subsequent speed changes.
   - Exclude the final 1 second of each interval to avoid transition noise.  
   ⬇️ In this example:
     - Range 1: 0–59s
     - Range 2: 90–179s
     - Range 3: 190–299s  
     *(Configurable in `config.yaml`)*

2. **Fit a linear polynomial to each range**:  
   For each range:
   
       y₁ = a₁x + b₁
       y₂ = a₂x + b₂
       y₃ = a₃x + b₃

3. **Correct the first range**:  
    $F_{ireal} = F_i - a_1·i$

4. **Correct later ranges cumulatively**:    
    $F_{ireal} = F_i - a_n·(i - t_{n-1}) - ∑(a_k·Δt_k)$
   
    where `Δtₖ` is the time span of the `k`-th range.

5. **Use corrected signals for force calculations.**

---

## 3. Input Files

### 3.1 Raw Load Cell Data

- `.txt` file with **12 columns** (6 channels × 2 load cells).
- Each column represents a channel’s force readings over time.

---

### 3.2 Experiment Log (`log.xlsx`)

- File names must end with `log.xlsx` (e.g., `test log.xlsx`).
- Multiple logs can be scanned from a directory.

| Column | Description                        |
|--------|------------------------------------|
| 1      | Motor frequency (Hz)               |
| 2      | Test start time (s)                |
| 3      | Test end time (s, optional)        |
| 4      | Average temperature (°C)           |
| 5      | Raw data file name                 |

![image](https://github.com/user-attachments/assets/8894b23f-314d-4d42-9677-eac1d8825a98)

📌 *If two test segments share the same data file, the second can leave the file name blank.*

📌 Temperature-to-density conversion uses:  
[Engineering Toolbox - Air Density](https://www.engineeringtoolbox.com/air-density-specific-weight-d_600.html)

---

### 3.3 Configuration File (`config.yaml`)

#### `Data_reading` section:

| Parameter                 | Description |
|---------------------------|-------------|
| `WindSpeed_relationship`  | Formula to convert motor speed to wind speed (e.g., `y = 0.84x`). Use `y = x` if wind speed is already in log. |
| `Sample_rate`             | Recording rate (Hz) |
| `Stable_time_0Hz`         | Settling time after starting from 0 m/s (recommended: ~30s) |
| `Stable_time_others`      | Settling time after other changes (recommended: 10s) |
| `Gap_before_next_wind_speed` | Data ignored before wind speed change (recommended: 1s) |

#### `Data_calculation` section:

| Parameter             | Unit | Description                  |
|-----------------------|------|------------------------------|
| `cylinder_diameter`   | m    | Diameter of test model       |
| `test_section_length` | m    | Length of the force measurement section |

---


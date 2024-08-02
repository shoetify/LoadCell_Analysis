from Util import LoadCell_Util
import numpy as np


class DataAnalyzer:
    @staticmethod
    def analyze(proceeded_tables, sample_rate, stable_time_others, stable_time_0Hz):

        proceeding_file_name = ''
        start_time, end_time = 0, 0
        time_series = []
        mean_force_tables = []
        rms_force_tables = []

        for table in proceeded_tables:

            raw_data = [[] for _ in range(4)]
            accumulated_error = [0 for _ in range(4)]
            mean_force_table = []
            rms_force_table = []

            proceeding_file_name = ''
            for i in range(len(table[0])):

                # These two list is to store each calculated mean and rms value and store back to force_table.
                mean_force = []
                rms_force = []

                # If it's a new file name, then read the file.
                if proceeding_file_name != table[3][i]:
                    proceeding_file_name = table[3][i]
                    column = LoadCell_Util.read_txt_file(proceeding_file_name)
                    raw_data[0], raw_data[1], raw_data[2], raw_data[3] = column[0], column[1], column[6], column[7]
                    column.clear()

                print(f'For wind speed {table[0][i]}')

                start_time, end_time = table[1][i], table[2][i]
                time_series = list(range(start_time * sample_rate, end_time * sample_rate + 1))

                print(f"length of the raw data is:{len(raw_data[0])}")

                for j in range(4):
                    print(f"For the {j} column of data")
                    print(f"    start time is: {start_time}, end time is:{end_time}, sample rate is:{sample_rate}")

                    data = raw_data[j][start_time * sample_rate: end_time * sample_rate + 1]
                    slope, intercept = LoadCell_Util.linear_fit(time_series, data)
                    print(f"    Slope: {slope}, Intercept: {intercept}")

                    for k in range(len(data)):
                        data[k] = data[k] - accumulated_error[j] - slope * k

                    mean_force.append(np.mean(data))
                    rms_force.append(np.sqrt(np.mean(np.square(data))))

                    print(
                        f"    mean value after correction is: {mean_force[-1]}; RMS value after correction is: "
                        f"{rms_force[-1]}")

                    test_time = stable_time_others
                    if table[0][i] < 0.1:
                        test_time = stable_time_0Hz
                    accumulated_error[j] += slope * (end_time - start_time + test_time) * sample_rate
                    print(f"    accumulated error is: {accumulated_error[j]}")

                mean_force_table.append([abs(mean_force[0] - mean_force[2]), mean_force[1] + mean_force[3]])
                rms_force_table.append(rms_force)

                print(' ')

            # Put the result back to force_tables
            mean_force_tables.append(mean_force_table)
            rms_force_tables.append(rms_force_table)

        return (mean_force_tables, rms_force_tables)
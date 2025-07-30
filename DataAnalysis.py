from Util import LoadCell_Util
import numpy as np


class DataAnalyzer:
    INDICATOR = ["Load-Cell 1's horizontal",
                 "Load-Cell 1's vertical",
                 "Load-Cell 2's horizontal",
                 "Load-Cell 2's vertical"]

    @staticmethod
    def analyze(proceeded_table, sample_rate, stable_time_others, stable_time_0Hz, deg, average, filter_freq):

        raw_data = [[] for _ in range(4)]
        accumulated_error = [0 for _ in range(4)]
        mean_force_table = []
        rms_force_table = []

        proceeding_file_name = ''
        for i in range(len(proceeded_table[0])):

            # These two list is to store each calculated mean and rms value and store back to force_table.
            mean_force = []
            rms_force = []

            # If it's a new file name, then read the file.
            if proceeding_file_name != proceeded_table[5][i]:
                proceeding_file_name = proceeded_table[5][i]
                raw_data = DataAnalyzer.read_new_file(proceeding_file_name)
                if average > 1:
                    raw_data = DataAnalyzer.average_point(raw_data, average)
                    sample_rate = int(sample_rate / average)
                if filter_freq > (sample_rate // 2):
                    raise TypeError(
                        'filtered frequency is larger than cutoff frequency. '
                        'Please check terms "Data_reading -> Sample_rate" and "Data_calculation -> filtered_frequency"')
                if filter_freq > 0.01:
                    raw_data = LoadCell_Util.low_pass_filter(raw_data, filter_freq, sample_rate)
                    print(f"    filtered_frequency: {filter_freq}")

            print(f'Start analyse wind speed: {proceeded_table[0][i]}')

            start_time, end_time = proceeded_table[1][i], proceeded_table[2][i]
            time_series = list(range(start_time * sample_rate, end_time * sample_rate + 1))
            for j in range(4):
                print(f"Analysing {DataAnalyzer.INDICATOR[j]} data")
                print(f"    Start time is:{start_time}s; End time is:{end_time}s")

                # Get the data in the time range, linear fit and fix the data according to the result of linear fit.
                data = raw_data[j][start_time * sample_rate: end_time * sample_rate + 1]
                coef = LoadCell_Util.poly_fit(time_series, data, deg)
                print(f"    Poly fit result is: " + ", ".join(map(str, coef)))
                de_data = DataAnalyzer.deduct_error(data, accumulated_error[j], coef, start_time * sample_rate)

                # Calculate mean and RMS value of Data
                mean_value = np.mean(de_data)
                mean_force.append(mean_value)
                for k in range(len(de_data)):
                    de_data[k] = de_data[k] - mean_value
                rms_force.append(np.sqrt(np.mean(np.square(de_data))))
                print(
                    f"    mean value after correction is: {mean_force[-1]}; RMS value after correction is: "
                    f"{rms_force[-1]}")

                # Calculate accumulate error
                test_time = stable_time_others
                if proceeded_table[0][i] < 0.1:
                    test_time = stable_time_0Hz
                operate_time = (end_time - start_time) * sample_rate
                for k in range(len(coef) - 1):
                    accumulated_error[j] += coef[k] * ((end_time + test_time) * sample_rate) ** (len(coef) - 1 - k)
                    accumulated_error[j] -= coef[k] * (start_time * sample_rate) ** (len(coef) - 1 - k)
                # accumulated_error[j] += slope * (end_time - start_time + test_time) * sample_rate
                print(f"    accumulated error is: {accumulated_error[j]}")

            mean_force_table.append(
                [abs(mean_force[0] - mean_force[2]), mean_force[1] + mean_force[3], mean_force[0], mean_force[1],
                 mean_force[2], mean_force[3]])
            rms_force_table.append(rms_force)
            print(' ')

        return mean_force_table, rms_force_table

    @staticmethod
    def read_new_file(file_name):
        data = []
        column = LoadCell_Util.read_txt_file(file_name)
        data.append(column[0])
        data.append(column[1])
        data.append(column[6])
        data.append(column[7])
        column.clear()
        return data

    @staticmethod
    def deduct_error(data, accumulated_error, coef, start):
        for k in range(len(data)):
            data[k] = data[k] - accumulated_error
            for l in range(len(coef) - 1):
                data[k] = data[k] - coef[l] * ((start + k) ** (len(coef) - 1 - l)) + coef[l] * (
                        start ** (len(coef) - 1 - l))
        return data

    @staticmethod
    def average_point(raw_datas, average):
        results = []
        for raw_data in raw_datas:
            result = []
            for j in range(int(len(raw_data) / average)):
                result.append(np.mean(raw_data[j * average:j * average + average]))
            if len(raw_data) % average != 0:
                result.append(np.mean(raw_data[j * average + average:]))
            results.append(result)
        return results

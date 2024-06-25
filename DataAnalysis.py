from Util import LoadCell_Util


class DataAnalyzer:
    @staticmethod
    def analyze(proceeded_tables, sample_rate):
        raw_data = [[] for _ in range(4)]
        proceeding_file_name = ''
        start_time, end_time = 0, 0
        time_series = []


        for table in proceeded_tables:
            proceeding_file_name = ''
            for i in range(len(table[0])):
                # If it's a new file name, then read the file.
                if proceeding_file_name != table[3][i]:
                    proceeding_file_name = table[3][i]
                    column = LoadCell_Util.read_txt_file(proceeding_file_name)
                    raw_data[0], raw_data[1], raw_data[2], raw_data[3] = column[0], column[1], column[6], column[7]
                    column.clear()

                print(f'For wind speed {table[0][i]}')

                start_time, end_time = table[1][i], table[2][i]
                time_series = list(range(start_time * sample_rate, end_time * sample_rate + 1))
                slopes = []
                intercepts = []
                for j in range(4):
                    data = raw_data[i][start_time * sample_rate: end_time * sample_rate + 1]
                    slope, intercept = LoadCell_Util.linear_fit(time_series, data)
                    print(f"Slope: {slope}, Intercept: {intercept}")
                    slopes.append(slope)
                    intercepts.append(intercept)


                print(' ')

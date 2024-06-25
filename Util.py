import re
import numpy as np

class LoadCell_Util:
    @staticmethod
    def parse_markdown(md_file_path):
        """
        This function reads a markdown file, identifies tables following "## Note" sections,
        and extracts the data into lists.

        :param md_file_path: Path to the markdown file.
        :return: A list of tables, where each table is represented as a list of three lists
                 (wind_speed, start_time, file_name).
        """
        with open(md_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Variables to store data
        wind_speed = []
        start_time = []
        end_time = []
        file_name = []

        # Flags and temporary storage
        in_table = False
        tables = []

        for line in lines:
            line = line.strip()

            if line.startswith("## Note"):
                in_table = False  # Reset the table flag for new notes

            if in_table:
                if line.startswith("|"):
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]

                    if len(cells) == 4:
                        wind_speed.append(cells[0])
                        start_time.append(cells[1])
                        end_time.append(cells[2])
                        file_name.append(cells[3])

                else:
                    in_table = False  # End of the table
                    # Save the table data to the list of tables
                    if wind_speed or start_time or end_time or file_name:
                        tables.append([wind_speed.copy(), start_time.copy(), end_time.copy(), file_name.copy()])
                        # Clear the lists for the next table
                        wind_speed.clear()
                        start_time.clear()
                        end_time.clear()
                        file_name.clear()
            elif line.startswith("| ---"):
                in_table = True  # Table detected

        return tables

    @staticmethod
    def read_txt_file(file_path):
        """
        Reads a .txt file where each row contains 12 columns separated by tabs or spaces,
        and returns each column as a separate list.

        :param file_path: Path to the .txt file.
        :return: A tuple of lists, where each list contains the values of a respective column.
        """
        columns = [[] for _ in range(12)]  # Create 12 empty lists for each column

        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():  # Check if the line is not empty
                    values = line.split()  # Split by whitespace (default behavior)
                    for idx, value in enumerate(values):
                        columns[idx].append(float(value))  # Convert to float and append to respective column list

        return columns

    @staticmethod
    def extract_numbers_from_string(string):

        """
        This function recognize all the number in the string and return a list of number.

        :param string: A string with numbers (e.g., "y=0.1726x-0.06956").
        :return: A list of float number representing the numbers in the string.
        """

        pattern = r'-?\d+\.?\d*'
        numbers = re.findall(pattern, string)
        return [float(num) for num in numbers]

    @staticmethod
    def motor_to_wind_speed(motorHz, wind_speed_a, wind_speed_b):

        """
        This function transfer the motor speed(Hz) into the real wind speed in wind tunnel.

        :param: motorHz: float, the motor speed in Hz;
                wind_speed_a: float, the wind speed coefficient get from config file;
                wind_speed_b: float, the wind speed coefficient get from config file;
        :return: float, the calculated real wind speed in wind tunnel.
        """

        if motorHz == 0.0:
            return 0.0
        else:
            return motorHz * wind_speed_a + wind_speed_b

    @staticmethod
    def proceed_table(tables, stable_time_0hz, stable_time_others, gap_before_next_wind_speed, wind_speed_a,
                      wind_speed_b):

        """
        Process the extracted tables from markdown and transform the data.

        This function processes the tables by transforming motor speed to wind speed,
        calculating start and end times based on given parameters, and ensuring
        file names are correctly assigned.

        Parameters:
        tables (list): List of tables extracted from the markdown file.
        stable_time_0hz (int): Stable time to add when wind speed is 0 Hz.
        stable_time_others (int): Stable time to add for other wind speeds.
        gap_before_next_wind_speed (int): Gap time to subtract before the next wind speed measurement.
        wind_speed_a (float): Coefficient 'a' for transforming motor speed to wind speed.
        wind_speed_b (float): Coefficient 'b' for transforming motor speed to wind speed.

        Returns:
        list: A list of processed tables with wind speed, start time, end time, and file name.

        Raises:
        TypeError: If any required cell in the input table is empty or has invalid data.
        """

        print('Proceeding lab log data ... ')
        proceed_tables = [[] for _ in range(4)]
        table_count = 0
        for table in tables:
            table_count += 1
            print('Proceeding lab log table ' + str(table_count) + ' ...')
            wind_speed = []
            start_time = []
            end_time = []
            file_name = []
            for i in range(len(table[0])):
                # Transform the motor speed to wind speed
                if not table[0][i]:
                    raise TypeError('Wind_Speed Cell is empty!!! Location: [' + str(i) + '] ...')
                wind_speed.append(LoadCell_Util.motor_to_wind_speed(float(table[0][i]), wind_speed_a, wind_speed_b))

                # Transform the recorded start time to calculated start time
                if not table[1][i]:
                    raise TypeError('Start_Time Cell is empty!!! Location: [' + str(i) + '] ...')
                if len(wind_speed) > 1 and wind_speed[-2] == 0.0:
                    # If the wind speed is start from 0m/s, then the calculated time should be added "stable_time_0hz"
                    start_time.append(int(table[1][i]) + stable_time_0hz)
                else:
                    # Otherwise, the calculated time should be added "stable_time_others"
                    start_time.append(int(table[1][i]) + stable_time_others)

                # Transform the recorded end time to calculated end time
                if table[2][i]:
                    end_time.append(int(table[2][i]) - gap_before_next_wind_speed)
                else:
                    # If end time is null, then set the next start time as this end time.
                    if table[1][i + 1]:
                        end_time.append(int(table[1][i + 1]) - gap_before_next_wind_speed)
                    else:
                        raise TypeError('End_Time Cell Error, cannot find when it is finish!!! Location: [' + str(i) +
                                        '] ...')
                # Double check if the end time is earlier than start time, then raise error.
                if end_time[-1] <= start_time[-1]:
                    raise TypeError('End Time is smaller than Start Time!!! Location: [' + str(i) + '] ...')

                # Transform the recorded file name to real file name.
                if table[3][i]:
                    file_name.append(table[3][i] + '.txt')
                else:
                    if len(file_name) > 0:
                        file_name.append(file_name[-1])
                    else:
                        raise TypeError('File_Name Cell Error, cannot find file name!!! Location: [' + str(i) + '] ...')

            proceed_tables[0] += wind_speed
            proceed_tables[1] += start_time
            proceed_tables[2] += end_time
            proceed_tables[3] += file_name
            # proceed_tables.append([wind_speed, start_time, end_time, file_name])

            print('Successfully proceeding lab log table ' + str(table_count) + ' ...')

        return proceed_tables

    @staticmethod
    def linear_fit(x_axis, y_axis):

        """
        Performs a linear fit on the given data points.

        This function takes two lists of equal length representing the x and y coordinates of data points,
        and calculates the slope and intercept of the best-fit line using a linear polynomial fit.

        Parameters:
        x_axis (list): A list of x-axis values (independent variable).
        y_axis (list): A list of y-axis values (dependent variable).

        Returns:
        tuple: A tuple containing the slope and intercept of the best-fit line.

        Example:
        x_axis = [1, 2, 3, 4]
        y_axis = [2, 3, 5, 7]
        slope, intercept = LoadCell_Util.linear_fit(x_axis, y_axis)
        """

        x = np.array(x_axis)
        y = np.array(y_axis)

        # Perform linear fit (degree 1 polynomial)
        coefficients = np.polyfit(x, y, 1)
        slope, intercept = coefficients

        return slope, intercept

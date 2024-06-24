import re


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

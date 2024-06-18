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

                    if len(cells) == 3:
                        wind_speed.append(cells[0])
                        start_time.append(cells[1])
                        file_name.append(cells[2])

                else:
                    in_table = False  # End of the table
                    # Save the table data to the list of tables
                    if wind_speed or start_time or file_name:
                        tables.append([wind_speed.copy(), start_time.copy(), file_name.copy()])
                        # Clear the lists for the next table
                        wind_speed.clear()
                        start_time.clear()
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
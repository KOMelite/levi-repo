from datetime import datetime
import os


def get_file_name(src):
        return os.path.split(src)[1].split('.')[0]

def determine_year():
    while True:
        current_year = datetime.now().year
        is_current_year = input(f"Is this the correct year '{current_year}' y/n : ")
        try:
            if is_current_year[0].lower() == "y":
                return current_year

            elif is_current_year[0].lower() == "n":
                return manually_set_year()

            else:
                raise ValueError

        except (IndexError, ValueError):
            print(f"""Unrecognized command '{is_current_year}'... Please enter a 'yes' or 'no' """)
            continue


def manually_set_year():
    year_character_limit = 4
    try:
        # if year is less than 1676 pandas library freaks out
        year = int(input("Insert correct year for this book: "))
        str_year = str(year)
        if len(str_year) != year_character_limit:
            raise ValueError
        return year

    except ValueError:
        print(f"Year must contain 4 digits... example(2021/2043/1875 etc)")
        return manually_set_year()


def check_column_merged(column_to_check, expected_characters):
    merged_rows_count = 0
    merged_rows_threshold = 15
    is_column_merged = False

    for row in column_to_check:
        if len(row) > expected_characters:
            merged_rows_count += 1

            if merged_rows_count >= merged_rows_threshold:
                is_column_merged = True
                return is_column_merged

    return is_column_merged

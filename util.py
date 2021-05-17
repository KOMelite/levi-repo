from datetime import datetime


def prompt_file_path(file_type: str):
    path = input(fr"{file_type} file path: ").strip('"')
    if valid_path(path):
        return path


# TODO add functionality to validate path
def valid_path(path):
    return True


def determine_year():
    print("Are we using the 'current' year for this book: ")

    while True:
        is_current_year = input("y/n : ")
        try:
            if is_current_year[0].lower() == "y":
                year = datetime.now().year
                year = str(year)
                return year

            elif is_current_year[0].lower() == "n":
                year = manually_set_year()
                return year

            else:
                raise ValueError

        except (IndexError, ValueError):
            print(f"""Unrecognized command '{is_current_year}'... Please enter a 'yes' or 'no' """)
            continue


def manually_set_year():
    year_character_limit = 4
    try:
        # if year is less than 1676 pandas library freaks out
        year = int(input("Insert year for this book: "))
        year = str(year)
        if len(year) != year_character_limit:
            raise ValueError
        return year

    except ValueError:
        print(f"Year must contain 4 digits... example(2021/2043/1875 etc)")
        return manually_set_year()

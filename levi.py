import camelot
import sys

import pandas as pd


def convert_pdf_to_dataframe(bank_document):
    print("\n\t\tAnalyzing Bank Document...")

    column_separators = ['50, 400, 480, 563']
    try:
        tables = camelot.read_pdf(bank_document,
                                  pages="2-end",
                                  flavor="stream",
                                  suppress_stdout=True,
                                  multiple_sheets=True,
                                  edge_tol=500,
                                  columns=column_separators)

        # .df is a property of TableList objects (Convert table to dataframe)
        data_frames = [table.df for table in tables]
        return pd.concat(data_frames)

    except FileNotFoundError:
        print("File has not been found make sure there is no typo in path name... \n")
        print(bank_document)
        print("Program force close")
        sys.exit()
    except NotImplementedError:
        print("Please make double sure the file PATH is to a PDF bank document")
        print("       Program force close... Can't interpret PDF PATH")
        sys.exit()


def splice_into_series(series, insert_pos: int, string_to_insert: str):
    if isinstance(series, str):
        edited_string = series[:insert_pos] + string_to_insert + series[insert_pos:]
        return edited_string

    else:
        tmp_list = []

        for old_string in series:
            if len(old_string) >= insert_pos:
                tmp_list.append(old_string[:insert_pos] + string_to_insert + old_string[insert_pos:])
            else:
                tmp_list.append(old_string)
        return tmp_list


def format_dates(dates, year):
    str_year = ' ' + str(year)
    character_offset = 6

    edited_dates = splice_into_series(series=dates,
                                      insert_pos=character_offset,
                                      string_to_insert=str_year)

    return pd.to_datetime(edited_dates, errors='coerce', format='%d %b %Y')


def separate_credit_from_debit(dataframe, column_name):
    credit = pd.to_numeric(column_name, errors="coerce", downcast="float").isna()
    credit = dataframe[credit].copy()

    debit = pd.to_numeric(column_name, errors="coerce", downcast="float").notna()
    debit = dataframe[debit].copy()

    return credit, debit


def calculate_vat(series, vat_percent):
    standard_value = 100
    vat_divisor = vat_percent + standard_value
    return [round((amount * vat_percent) / vat_divisor, 2) for amount in series]


def calculate_exclusive_vat(series, vat_percent):
    standard_value = 100
    vat_divisor = vat_percent + standard_value
    return [round((amount * standard_value) / vat_divisor, 2) for amount in series]


def to_excel(df_credit, df_debit, excel_path):
    try:
        with pd.ExcelWriter(excel_path,
                            mode='a') as writer:
            df_credit.to_excel(writer,
                               index=False,
                               sheet_name='Credit')
            df_debit.to_excel(writer,
                              index=False,
                              sheet_name='Debit')

        print("All finished thank you for using Levi!")
    except FileNotFoundError:
        print("Check for typo in Excel PATH as the file could not be found... \n")
        print(excel_path)
        print("     Program force close... Can't Find Excel File")
        sys.exit()
    except ValueError:
        print("Please make double sure the file PATH is to an existing Excel document... \n")
        print("     Program force close... Can't interpret Excel PATH")
        sys.exit()

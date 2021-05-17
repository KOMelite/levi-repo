import camelot
import sys

import pandas as pd
from datetime import datetime


def convert_pdf_to_dataframe(bank_document):

    print("\n                  Analyzing Bank Document...")

    columns_separators = ['50, 400, 480, 563']
    try:
        tables = camelot.read_pdf(bank_document,
                                  pages="2-end",
                                  flavor="stream",
                                  suppress_stdout=True,
                                  multiple_sheets=True,
                                  edge_tol=500,
                                  columns=columns_separators)

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


# Main Trunk
def structure_dataframe(df, str_year):
    """
    Main "Trunk" of code responsible for structuring the dataframe from which other functions / branches
    spread out from.

    :param df: Data Frame
    :param str_year: year to format date column

    :return: DataFrame tuple (credit_df, debit_df) after being processed by format_amount() function
    """

    print("\n          Formatting and structuring data... Almost done :) \n")

    df = df.iloc[2:].copy()  # Removes the first 3 lines from dataframe

    # High priority function
    # Formats date as well as removes gaps between tables must run first in program
    df = format_date_column(df, str_year)

    # Only after format_date_column can we assign header names
    # Drop_1 and Drop_2 are pieces of information that are not needed
    df.columns = ["DATE", "DESCRIPTION", "AMOUNT", "Drop_1", "Drop_2"]

    # Drops unwanted columns
    items_to_drop = ['Drop_1', 'Drop_2']
    df.drop(items_to_drop,
            axis=1,
            inplace=True)

    # Last thing to do is to format the amount column
    # Returns two dataframes to main.py
    df_tuple = format_amount(df)
    return df_tuple


# Branch function for structure_dataframe()
def format_date_column(df, str_year):
    """
     --FORMAT DATE COLUMN--
    This function must run first as it not only formats the dates...
    but also removes unwanted data from table, via usage of the date column.

    As well as splitting col_1 and col_2 if they where read in as a single column, the function
    structure_dates() determines this and places a comma where the separation needs to occur

    :param df: Data Frame
    :param str_year: year to format date column

    :return: edited Data Frame
    """

    df.rename({0: "Dates"}, axis=1, inplace=True)  # Renames column df[0] too "Date", for ease of use

    # Pass each "Dates" element through function structure_dates()
    # If data is merged it will be separated by a comma
    df["Dates"] = [structure_dates(date_element, str_year) for date_element in df["Dates"]]

    # Check date column to see if a comma was implemented to split the date + adjacent column
    comma_count = 0
    comma_threshold = 20

    for date_element in df["Dates"]:
        if comma_count > comma_threshold:
            break
        elif "," in date_element:
            comma_count += 1

    # If true... run str.split() method splits the joined columns by comma
    if comma_count > comma_threshold:
        df["Dates"] = df["Dates"].str.split(pat=",", expand=True)

    # Date should be formatted as DD MMM YYYY (MMM = Jan, Feb, Mar...)
    # Convert to datetime format if date cant be converted to datetime convert to NaN instead
    df["Dates"] = pd.to_datetime(df["Dates"], errors='coerce', format='%d %b %Y')

    # Remove entire row that contains NaN value in date column
    # Drops all non-essential data between tables
    df = df.dropna(subset=["Dates"]).copy()

    # Convert date time objects to string objects in correctly formatted style
    df["Dates"] = [datetime.strftime(date_element, "%d/%m/%Y") for date_element in df["Dates"]]
    return df


# Branch function for format_date_column()
def structure_dates(date, year):
    """
    Appends the variable year(string) to the date column, sometimes col_1 and col_2 merge by accident,
    if columns merged count 6 characters and insert year in the middle of the two and add a comma to latter
    use to split these two accidentally merged columns.

    :param date: Series from Data Frame
    :param year: year to format date column

    :return: Series [date column] - formatted
    """
    # Using list comprehension to dynamically format date column
    # Where "date" parameter is each element in date column
    max_char = 6

    # If length of object is longer than max_char... then date column has merged with adjacent column
    # DD MMM = 6 characters including the space between
    if len(date) > max_char:

        # Insert "string" after the 6th character "max_char"
        # Formula = a_string[:i] + "add_to_string" + a_string[i:]
        # Notice the addition of the comma if length of date element exceeds 6 characters
        date = date[:max_char] + f" {year}," + date[max_char:]
        return date

    # Date column has not merged with adjacent column just append the year to element
    else:
        date = date + f" {year}"
        return date


# Branch function for structure_dataframe()
def format_amount(df):
    """
    Separates Data Frame into two distinct Data Frames namely (Credit and Debit)

    :param df: Data Frame
    :return: tuple (credit_df, debit_df)
    """

    # 1st removes all the silly commas placed in amount column
    df["AMOUNT"] = [amount_element.replace(",", "") for amount_element in df["AMOUNT"]]

    # Attempt to convert to numeric if item contains "Cr" it will be converted to NaN
    # isna() function only returns the values which are NaN.. ie.. credit in this case
    credit = pd.to_numeric(df["AMOUNT"], errors="coerce", downcast="float").isna()

    # --Credit--
    credit_df = df[credit].copy()
    credit_df["AMOUNT"] = [credit_element.replace("Cr", "") for credit_element in credit_df["AMOUNT"]]
    credit_df["AMOUNT"] = pd.to_numeric(credit_df["AMOUNT"], downcast='float')

    # --Debit--
    # Set up Vat variables
    vat_percent = 15
    vat_divisor = vat_percent + 100

    # Polar opposite of above, where function only returns the values which are *NOT* NaN.. ie.. debit
    debit = pd.to_numeric(df["AMOUNT"], errors="coerce", downcast="float").notna()

    debit_df = df[debit].copy()
    debit_df["AMOUNT"] = pd.to_numeric(debit_df["AMOUNT"], downcast="float")

    # Remove all 0.00 amounts from debits
    debit_df = debit_df[debit_df["AMOUNT"] > 0.00001]

    # Formula if vat at 15%: Vat(15%) = (amount * 15) / 115
    # Calculates the amount of vat on a item
    debit_df[f"VAT ({str(vat_percent)}%)"] = debit_df.apply(lambda row: row["AMOUNT"] * vat_percent / vat_divisor,
                                                            axis=1)

    # Formula if vat at 15%: Vat_Exclusive = (amount * 100) / 115
    # Calculates the amount without the vat
    debit_df["VAT EXCLUSIVE"] = debit_df.apply(lambda row: row["AMOUNT"] * 100 / vat_divisor,
                                               axis=1)

    return credit_df, debit_df


# Responsible for exporting dataframe to excel in proper format
def to_excel(df_credit, df_debit, excel_path):
    """Appends Data Frames (Credit and Debit) to target excel worksheet"""
    try:
        with pd.ExcelWriter(excel_path,
                            mode='a') as writer:
            df_credit.to_excel(writer,
                               index=False,
                               sheet_name='Credit')
            df_debit.to_excel(writer,
                              index=False,
                              sheet_name='Debit')

        # Print to user...
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


# Creates a csv file in program for visual debugging purposes...
def test_csv(credit_df, debit_df, dataframe):
    """Used for visual debugging if error encountered"""

    credit_df.to_csv("credit.csv")
    debit_df.to_csv("debit.csv")
    dataframe.to_csv("dataframe.csv")

    # levi.test_csv(df_credit, df_debit, df)

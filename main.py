import levi

from util import prompt_file_path
from util import determine_year

if __name__ == '__main__':

    bank_pdf = prompt_file_path("Bank PDF Document")
    excel = prompt_file_path("EXCEL")

    year = determine_year()

    df = levi.convert_pdf_to_dataframe(bank_pdf)

    # Step four: Structure dataframe for exporting to excel
    # Note df is now a tuple containing two dataframes... credit and debit
    df_tuple = levi.structure_dataframe(df, year)

    # Step five: Assign the two dataframes with in df_tuple + Export dataframe to excel
    df_credit, df_debit = df_tuple
    levi.to_excel(df_credit, df_debit, excel)

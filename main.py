import pandas as pd

from levi import (
    convert_pdf_to_dataframe,
    splice_into_series,
    format_dates,
    separate_credit_from_debit,
    to_excel,
    calculate_vat,
    calculate_exclusive_vat
)

from util import (
    prompt_file_path,
    determine_year,
    check_column_merged
)

if __name__ == '__main__':

    bank_pdf = prompt_file_path("Bank PDF Document")
    excel = prompt_file_path("EXCEL")

    year = determine_year()

    df = convert_pdf_to_dataframe(bank_pdf)

    df.dropna(how='any', inplace=True)
    df.rename({0: "Dates"}, axis=1, inplace=True)

    expected_characters = 6
    date_column_is_merged = check_column_merged(column_to_check=df["Dates"],
                                                expected_characters=expected_characters)

    if date_column_is_merged:
        df["Dates"] = splice_into_series(series=df["Dates"],
                                         insert_pos=expected_characters,
                                         string_to_insert=',')

        df["Dates"] = df["Dates"].str.split(",", expand=True)

    df["Dates"] = format_dates(df["Dates"], year)

    df = df.dropna(how='any')

    df.columns = ["DATE", "DESCRIPTION", "AMOUNT", "Drop_1", "Drop_2"]
    columns_to_drop = ['Drop_1', 'Drop_2']
    df.drop(columns_to_drop,
            axis=1,
            inplace=True)

    df["AMOUNT"] = [row.replace(",", "") for row in df["AMOUNT"]]
    
    credit, debit = separate_credit_from_debit(dataframe=df,
                                               column_name=df["AMOUNT"])
    credit["AMOUNT"] = [row.replace("Cr", "") for row in credit["AMOUNT"]]
    credit["AMOUNT"] = pd.to_numeric(credit["AMOUNT"], downcast='float')

    debit["AMOUNT"] = pd.to_numeric(debit["AMOUNT"], downcast="float")
    debit = debit[debit["AMOUNT"] > 0.00001]

    vat_percent = 15
    debit[f"VAT ({str(vat_percent)}%)"] = calculate_vat(debit["AMOUNT"], vat_percent)
    debit["VAT EXCLUSIVE"] = calculate_exclusive_vat(debit["AMOUNT"], vat_percent)

    to_excel(credit, debit, excel)

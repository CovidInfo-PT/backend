from gsheets.spreadsheet import SpreadSheet
from form_validator import FormValidator



if __name__ == '__main__':

    # create object to access the wanted spreadsheet
    spreadSheet = SpreadSheet()

    # open worksheet with index no. 1: "Validacao"
    worksheet = spreadSheet.get_worksheet('Validacao', 1)

    # get the companies' as a list of rows
    companies_rows = worksheet.get()

    # create a tuple witth the row and the row id. This information will be used for 
    # the error logging on the google sheet
    for i in range(0, len(companies_rows)):
        companies_rows[i] = (i, companies_rows[i])
    
    # ignore the header and filter the results to only obtain the rows with information
    companies_rows = filter(lambda row_tuple: row_tuple[1][0].strip() != '', companies_rows[1:])

    # delegate to the form validator to validate the data
    form_validator = FormValidator(spreadSheet, 28,companies_rows, 4, "../Data/added_companies_hashes", "../Data/counties/by_geohash", "../Data/counties/by_name")
    form_validator.process_form()
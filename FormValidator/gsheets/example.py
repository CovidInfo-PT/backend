from spreadsheet import SpreadSheet



if __name__ == '__main__':

    # create object to access "Validacao_VersaoTestes" spreadsheet
    spreadSheet = SpreadSheet()

    # open worksheet with index no. 1: "Validacao"
    worksheet = spreadSheet.get_worksheet('Validacao_VersaoTestes', 1)

    # check a specific cell of column no. 24
    spreadSheet.check_cell(20)

    # uncheck a specific cell of column no. 24
    spreadSheet.uncheck_cell(21)

    # write an error on a specific cell of column no. 25
    spreadSheet.write_error("error: another dumb error", 20)

    # write a json object error on cell (20, 26)
    spreadSheet.write_json_error({"error": "this is a json error"}, 20, 26)

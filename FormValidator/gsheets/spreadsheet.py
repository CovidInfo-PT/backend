import gspread
import pprint
import json
from oauth2client.service_account import ServiceAccountCredentials

class SpreadSheet:
    """
    Class to manipulate google spreadsheats using Google's API.
    """
    def __init__(self, credentials='credentials.json', name='Validacao_VersaoTestes', idx=1):
        """
        This constructor creates a client to interact with the google spreadsheet
        passed in the parameter. It needs a json file with API auth credentials.

        @param credentials: Google Sheets API authentication credentials
        @param name: spreadsheet name
        """

        self.scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials, self.scope)
        self.client = gspread.authorize(self.creds)

        # opens a specific worksheet
        self.worksheet = self.client.open(name).get_worksheet(idx)

    """
    This method opens and returns a specific worksheet
    """
    def get_worksheet(self, name='Validacao_VersaoTestes', idx=1):
        self.worksheet = self.client.open(name).get_worksheet(idx)
        return self.worksheet
    
    """
    This method checks a specific cell of col no. 24, 
    changing its value to 'TRUE'
    """
    def check_cell(self, row, col=24):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, 'TRUE')
    
    """
    This method unchecks a specific cell of col no. 24, 
    changing its value to 'TRUE'
    """
    def uncheck_cell(self, row, col=24):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, 'FALSE')
    
    """
    This method writes an error on a specific cell of default col no. 25
    """
    def write_error(self, error, row, col=25):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, error)

    """
    This method writes an json object error on a specific cell of default col no. 25
    """
    def write_json_error(self, error, row, col=25):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, json.dumps(error))


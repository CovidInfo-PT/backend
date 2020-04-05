import gspread
import pprint
import json
from oauth2client.service_account import ServiceAccountCredentials

class SpreadSheet:

    def __init__(self, credentials='credentials.json', name='Validacao_VersaoTestes', idx=1):
        
        self.scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials, self.scope)
        self.client = gspread.authorize(self.creds)

        self.worksheet = self.client.open(name).get_worksheet(idx)

    def get_worksheet(self, name='Validacao_VersaoTestes', idx=1):
        self.worksheet = self.client.open(name).get_worksheet(idx)
        return self.worksheet
    
    def check_cell(self, row, col=24):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, 'TRUE')
    
    def uncheck_cell(self, row, col=24):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, 'FALSE')
    
    def write_error(self, error, row, col=25):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, error)

    def write_json_error(self, error, row, col=25):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, json.dumps(error))


import gspread
import pprint
from oauth2client.service_account import ServiceAccountCredentials

class SpreadSheet:

    def __init__(self, credentials='credentials.json', name='Validacao_VersaoTestes'):
        
        self.scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials, self.scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(name)

    def open_worksheet(self, name='Validacao_VersaoTestes', idx=1):
        self.worksheet = self.client.open(name).get_worksheet(idx)
        return self.worksheet
    
    def check_cell(self, row, col=24):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, 'TRUE')
    
    def uncheck_cell(self, row, col=24):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, 'FALSE')
    
    def write_error(self, row, col=25, error="error"):
        if row > 0 and col > 0:
            self.worksheet.update_cell(row, col, error)
    


import gspread
import pprint
from oauth2client.service_account import ServiceAccountCredentials

sheet = 'https://spreadsheets.google.com/feeds'

scope = [sheet,'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

sheet = client.open('Validacao_VersaoTestes').get_worksheet(1)
pp = pprint.PrettyPrinter()

print(dir(sheet))

pp.pprint(sheet.get_all_records())

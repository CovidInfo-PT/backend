from gsheets.spreadsheet import SpreadSheet
from form_validator import FormValidator
from globalLog import GlobalLogger
import configparser
import argparse
import logging
import os


"""
Will load all the properties needed to run the program from a properties file
"""
def load_configs(config_path):
    config = configparser.RawConfigParser()
    config.read(config_path)
    
    # create properties dic
    properties_dic = {}
    error = False
    try:
        properties_dic["sheet_name"] = config.get('FormGoogleSheets', 'sheet_name')
        properties_dic["sheet_index"] = int(config.get('FormGoogleSheets', 'sheet_index'))
        properties_dic["error_column"] = int(config.get('FormGoogleSheets', 'error_column'))
        properties_dic["validated_checkbox_column"] = int(config.get('FormGoogleSheets', 'validated_checkbox_column'))
        properties_dic["added_companies_path"] = config.get('DataFiles', 'added_companies_path')
        properties_dic["counties_by_geohash_dir_path"] = config.get('DataFiles', 'counties_by_geohash_dir_path')
        properties_dic["counties_by_name_dir_path"] = config.get('DataFiles', 'counties_by_name_dir_path')
        properties_dic["bytes_per_county_geohassh"] = int(config.get('DataFiles', 'bytes_per_county_geohassh'))

        properties_dic["global_logger_path"] = config.get('Logger', 'global_logger_path')
        properties_dic["form_validator_logger_path"] = config.get('Logger', 'form_validator_logger_path')
        properties_dic["company_validator_logger_path"] = config.get('Logger', 'company_validator_logger_path')

    except:
        error = True
    return error, properties_dic


"""
Parse the arguments and return them
"""
def parse_arguments():
     # add arguments parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest='properties_path', help="Properties File")
    results = parser.parse_args()

    # Check if properties were passed
    if results.properties_path == None:
        print("[Error] No properties were passed as an argument")
        print("Usage updateCompanies.py -p <path to properties file> ")
        exit(1)

    # check if file exist
    if not os.path.isfile(results.properties_path):
        print("[Error] Incorrect path")
        print("Usage updateCompanies.py -p <path to properties file> ")
        exit(1)

    # return the properties' file location
    return results.properties_path


if __name__ == '__main__':
    # parse the arguments
    propeties_file_path = parse_arguments()

    # load the properties
    occured_error, properties = load_configs(propeties_file_path)
    if(occured_error):
        print("[Error] Error parsing the properties file")
        exit(1)

    # set global logger mechanism
    globalLogger = GlobalLogger(properties["global_logger_path"])

    logging.getLogger('UpdateCompany')

    # create object to access the wanted spreadsheet
    spreadSheet = SpreadSheet()

    # open worksheet with index no. 1: "Validacao"
    worksheet = spreadSheet.get_worksheet(properties['sheet_name'], properties['sheet_index'])

    # get the companies' as a list of rows
    companies_rows = worksheet.get()

    # create a tuple witth the row and the row id. This information will be used for 
    # the error logging on the google sheet
    for i in range(0, len(companies_rows)):
        companies_rows[i] = (i, companies_rows[i])
    
    # ignore the header and filter the results to only obtain the rows with information
    companies_rows = filter(lambda row_tuple: row_tuple[1][0].strip() != '', companies_rows[1:])

    # delegate to the form validator to validate the data
    form_validator = FormValidator(properties["form_validator_logger_path"], properties["company_validator_logger_path"], globalLogger, spreadSheet,  properties['error_column'], properties['validated_checkbox_column'], companies_rows, properties["bytes_per_county_geohassh"], properties["added_companies_path"], properties["counties_by_geohash_dir_path"], properties["counties_by_name_dir_path"])
    form_validator.process_form()



   



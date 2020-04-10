# add base directory to the path from where we can import
from sys import path
from os import getcwd
path.append(getcwd() + "/..")
from FormValidator.gsheets.spreadsheet import SpreadSheet
from FormValidator.form_validator import FormValidator
from FormValidator.globalLog import GlobalLogger
from backups.backup import BackupJob
import time
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
        # Forms Google Sheet info
        properties_dic["googlesheets_credentials_file_path"] = config.get('FormGoogleSheets', 'googlesheets_credentials_file_path')    
        properties_dic["sheet_name"] = config.get('FormGoogleSheets', 'sheet_name')
        properties_dic["sheet_index"] = int(config.get('FormGoogleSheets', 'sheet_index'))
        properties_dic["error_column"] = int(config.get('FormGoogleSheets', 'error_column'))
        x, y = config.get('FormGoogleSheets', 'timestamp_coords').split(",")
        properties_dic["timestamp_coords"] = (int(x), int(y))
        properties_dic["validated_checkbox_column"] = int(config.get('FormGoogleSheets', 'validated_checkbox_column'))

        # Datafiles info
        properties_dic["added_companies_path"] = config.get('DataFiles', 'added_companies_path')
        properties_dic["counties_by_geohash_dir_path"] = config.get('DataFiles', 'counties_by_geohash_dir_path')
        properties_dic["counties_by_name_dir_path"] = config.get('DataFiles', 'counties_by_name_dir_path')
        properties_dic["bytes_per_county_geohash"] = int(config.get('DataFiles', 'bytes_per_county_geohash'))

        # Logger infos
        properties_dic["global_logger_path"] = config.get('Logger', 'global_logger_path')
        properties_dic["form_validator_logger_path"] = config.get('Logger', 'form_validator_logger_path')
        properties_dic["company_validator_logger_path"] = config.get('Logger', 'company_validator_logger_path')
        
        # Backups info
        properties_dic["backups_output_dir"] = config.get('Backups', 'backups_output_dir')
        properties_dic["dirs_to_backup"] = config.get('Backups', 'dirs_to_backup').split(',')
        properties_dic["s3_backup_bucket"] = config.get('Backups', 's3_backup_bucket')
        
        # Cron job info
        properties_dic["period_minutes"] = int(config.get('Cronjob', 'period_minutes'))



        # Check all files and dirs
        if not os.path.isfile(properties_dic["added_companies_path"]):
            print("Invalid added_companies_path")
            error = True

        if not os.path.isfile(properties_dic["googlesheets_credentials_file_path"]):
            print("Invalid googlesheets_credentials_file_path")
            error = True

        if not os.path.isdir(properties_dic["counties_by_geohash_dir_path"]):
            print("Invalid counties_by_geohash_dir_path")
            error = True

        if not os.path.isdir(properties_dic["counties_by_name_dir_path"]):
            print("Invalid counties_by_name_dir_path")
            error = True

        if not os.path.isfile(properties_dic["global_logger_path"]):
            print("Invalid global_logger_path")
            error = True

        if not os.path.isfile(properties_dic["form_validator_logger_path"]):
            print("Invalid form_validator_logger_path")
            error = True

        if not os.path.isfile(properties_dic["company_validator_logger_path"]):
            print("Invalid company_validator_logger_path")
            error = True

        if not os.path.isdir(properties_dic["backups_output_dir"]):
            print("Invalid backups_output_dir")
            error = True

        for p in properties_dic["dirs_to_backup"]:
            if not os.path.isdir(p):
                print("Invalid dirs_to_backup - {}".format(p))
                error = True


        # check env variables for backups
        properties_dic["COVID_AWS_S3_ACCESS_KEY"] = os.getenv('COVID_AWS_S3_ACCESS_KEY')
        properties_dic["COVID_AWS_S3_SECRET_KEY"] = os.getenv('COVID_AWS_S3_SECRET_KEY')

        if properties_dic["COVID_AWS_S3_ACCESS_KEY"] == None:
            print("No env. variable COVID_AWS_S3_ACCESS_KEY")
            error = True

        if properties_dic["COVID_AWS_S3_SECRET_KEY"] == None:
            print("No env. variable COVID_AWS_S3_SECRET_KEY")
            error = True



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
        print("Usage deploy.py -p <path to properties file> ")
        exit(1)

    # check if file exist
    if not os.path.isfile(results.properties_path):
        print("[Error] Incorrect path")
        print("Usage deploy.py -p <path to properties file> ")
        exit(1)

    # return the properties' file location
    return results.properties_path


if __name__ == '__main__':
    # parse the arguments
    propeties_file_path = parse_arguments()

    # load the properties
    occured_error, properties = load_configs(propeties_file_path)
    if(occured_error):
        print("[Error] Error parsing the properties file or in getting env variables")
        exit(1)

    
    # set global logger mechanism
    globalLogger = GlobalLogger(properties["global_logger_path"])

    logging.getLogger('UpdateCompany')

    globalLogger.log(logging.INFO, 'Entering infinite loop', "DEPLOY")

    while True:

        # first, create a backup
        backup_job = BackupJob(properties["backups_output_dir"], properties["dirs_to_backup"], properties["s3_backup_bucket"])
        if not backup_job.make_backups():
            globalLogger.log(logging.INFO, 'Error on backing up the information'.format(properties["period_minutes"]), "DEPLOY")
            break

        # create object to access the wanted spreadsheet
        spreadSheet = SpreadSheet(credentials=properties["googlesheets_credentials_file_path"])

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
        form_validator = FormValidator(properties["form_validator_logger_path"], properties["company_validator_logger_path"], globalLogger, spreadSheet,  properties['error_column'], properties['validated_checkbox_column'], properties['timestamp_coords'], companies_rows, properties["bytes_per_county_geohash"], properties["added_companies_path"], properties["counties_by_geohash_dir_path"], properties["counties_by_name_dir_path"])
        form_validator.process_form()

        globalLogger.log(logging.INFO, 'Wait fot next update companies in {} minutes'.format(properties["period_minutes"]), "DEPLOY")
        time.sleep(properties["period_minutes"]*60)



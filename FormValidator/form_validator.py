from os import path, listdir
import csv
import json
import hashlib
import logging
from pathlib import Path
from company_validator import CompanyValidator
from geocoding.geocoding import Geocoding

class FormValidator:

    class_string_identifier = 'FormValidator'
    

    def __init__(self, class_logger_path, companies_logger_path, global_logger, google_sheet, error_col, validated_checkbox_column, row_tuples_list, geohash_county_bytes, added_companies_filename, counties_by_geohash_dirname, counties_by_name_dirname):
        self.class_logger_path = class_logger_path
        self.companies_logger_path = companies_logger_path
        self.global_logger = global_logger
        self.google_sheet = google_sheet
        self.error_col = error_col
        self.validated_checkbox_column = validated_checkbox_column
        self.row_tuples_list = row_tuples_list
        self.geohash_county_bytes = geohash_county_bytes
        self.added_companies_filename = added_companies_filename
        self.counties_by_geohash_dirname = counties_by_geohash_dirname
        self.counties_by_name_dirname = counties_by_name_dirname
        self.errors = []

        # set local logging mechanism

        self.logger = logging.getLogger('FormValidator')
        hdlr = logging.FileHandler(class_logger_path)
        formatter = logging.Formatter('[%(asctime)s | %(levelname)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.INFO)

        # create mechanismo to get the google url from address
        self.gmapsUrlGetter = Geocoding()


    """
    Processes all the companies in the csv document, checking if they contain errors, or are ok to move on
    to the database
    """
    def process_form(self):

        # get all the companies that have already been added (hash of the companies)
        self.added_companies_lst = self.get_added_companies_hashes()

        # Create a company validator
        company_validator = CompanyValidator(self.companies_logger_path, self.gmapsUrlGetter)
        self.logger.log(logging.INFO, 'Created company validator')
        self.global_logger.log(logging.INFO, 'Created company validator', self.class_string_identifier)

        # counter for the global log file
        already_inserted = 0
        added = 0
        with_error = 0

        self.global_logger.log(logging.INFO, 'Iterating through all the form entries', self.class_string_identifier)
        for row in self.row_tuples_list:
            row_id, row_data = row[0], row[1]

            # get company hash
            company_hash = hashlib.sha256((row_data[3] + row_data[4]).encode('utf-8')).hexdigest()
            self.logger.log(logging.INFO, 'Created hash for {} - {}'.format(row_data[3],row_data[4])) 

            # if the company doesnt exist yet, process it
            if  company_hash not in self.added_companies_lst:
                errors, company_dic = company_validator.process_company(row_data)
            
                # if there are no errors add the company to json
                if len(errors) == 0:
                    self.add_company(company_dic, company_hash)
                    self.google_sheet.check_cell(row=row_id+1, col=self.validated_checkbox_column)
                    added += 1
                # else print errors
                else:
                    print("[Company WAS NOT added to database] {} - {} | Errors={}".format(row_data[3],row_data[4], errors))  
                    self.logger.log(logging.INFO, "The company {} - {} was NOT added to database. Errors={}".format(row_data[3],row_data[4], errors)) 

                    # uncheck validation checkbox on google sheets
                    self.google_sheet.uncheck_cell(row=row_id+1, col=self.validated_checkbox_column)
                    self.logger.log(logging.INFO, "Uncheck the validation checkbox (google sheets) for the company  {} - {}".format(row_data[3],row_data[4])) 

                # write errors to google sheets
                self.google_sheet.write_error(error=str(errors), row=row_id+1, col=self.error_col)
                self.logger.log(logging.INFO, "Wrote the error on the google sheets, for the company  {} - {}".format(row_data[3],row_data[4])) 
                with_error +=1

            else:
                already_inserted += 1
                print("[Company already in database] {} - {}".format(row_data[3],row_data[4])) 
                self.logger.log(logging.INFO, "The company {} - {} was already in the database".format(row_data[3],row_data[4])) 

        self.global_logger.log(logging.INFO, 'Processed all the form entries', self.class_string_identifier)
        self.global_logger.log(logging.INFO, 'There were {} companies that were already in the database and were inserted {} new ones'.format(already_inserted, added), self.class_string_identifier)
        self.global_logger.log(logging.INFO, 'There were {} companies with errors'.format(with_error), self.class_string_identifier)


    """
    Given the company dic and the company hash, this function adds the company to the 'database'
    """
    def add_company(self, company_dic, company_hash):
        # set company id
        company_dic["id"] = company_hash

        # get county geohash
        geohash = company_dic["geo_hash"]
        county_geohash = geohash[:self.geohash_county_bytes]

        # if there is already a county json created with that hash
        # add the info in the counties_by_geohash dir and in the counties_by_name
        # the tuples here were created like (output_dir, identifier -> {identifier}.json, list of the identifiers of the output dir)
        for output_data in [ (self.counties_by_geohash_dirname, county_geohash, self.get_added_counties_jsons_names(self.counties_by_geohash_dirname)), (self.counties_by_name_dirname, company_dic["county"], self.get_added_counties_jsons_names(self.counties_by_name_dirname))]:
            poss_filename = "{}.json".format(output_data[1])
            if poss_filename in output_data[2]:
                # read json to memory and append to it
                f = open(Path(output_data[0], poss_filename))
                f_json_in_memory = json.loads(f.read())
                f_json_in_memory[company_hash] = company_dic 
                f.close()
                print("[Adding new company in existent county ({})] {} - {}".format(poss_filename, company_dic["parish"], company_dic["name"]))
                self.logger.log(logging.INFO, "Added new company in existent county ({}): {} - {}".format(poss_filename, company_dic["parish"], company_dic["name"]))
            else:
                f_json_in_memory = {company_hash:company_dic}
                print("[Adding new company in new county ({})] {} - {}".format(poss_filename, company_dic["parish"], company_dic["name"]))
                self.logger.log(logging.INFO, "Added new company in new county ({}):{} - {}".format(poss_filename, company_dic["parish"], company_dic["name"]))

            # parse to json
            f_json = json.dumps(f_json_in_memory, ensure_ascii=False).encode('utf8').decode("utf8")
            # write the data
            f = open(Path(output_data[0], poss_filename), 'w')
            f.write(f_json)
            f.close()
            self.logger.log(logging.INFO, "Written the data about the company {} - {}  to the file {}".format( company_dic["parish"], company_dic["name"], poss_filename))

        # add company hash to list of added companies
        f = open(self.added_companies_filename, "a")
        f.write(str(company_hash) + "\n")
        f.close()

        #add also to the list that is loaded to memory
        self.added_companies_lst.append(company_hash)
        

    """
    Gets a list of all the county jsons already created
    """
    def get_added_counties_jsons_names(self, dirname):
        files = []
        for f in listdir(dirname):
            if path.isfile(Path(dirname,f)):
                files.append(f)
        self.logger.log(logging.INFO, "Got all the added counties jsons from the file {}".format(dirname))
        return files


    """
    Gets a list of all the companies that are already in database
    """
    def get_added_companies_hashes(self):
        f = open(self.added_companies_filename)
        self.logger.log(logging.INFO, "Got all the added companies' geohashes from the file {}".format(self.added_companies_filename))
        return [line.strip() for line in f]

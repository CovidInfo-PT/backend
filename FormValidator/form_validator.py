from os import path, listdir
import csv
import json
import hashlib
from pathlib import Path
from company_validator import CompanyValidator


class FormValidator:

    def __init__(self, google_sheet, error_col, validated_checkbox_column, row_tuples_list, geohash_county_bytes, added_companies_filename, counties_by_geohash_dirname, counties_by_name_dirname):
        self.google_sheet = google_sheet
        self.error_col = error_col
        self.validated_checkbox_column = validated_checkbox_column
        self.row_tuples_list = row_tuples_list
        self.geohash_county_bytes = geohash_county_bytes
        self.added_companies_filename = added_companies_filename
        self.counties_by_geohash_dirname = counties_by_geohash_dirname
        self.counties_by_name_dirname = counties_by_name_dirname
        self.errors = []
 
    """
    Processes all the companies in the csv document, checking if they contain errors, or are ok to move on
    to the database
    """
    def process_form(self):

        # get all the companies that have already been added (hash of the companies)
        self.added_companies_lst = self.get_added_companies_hashes()

        # Create a company validator
        company_validator = CompanyValidator()

        for row in self.row_tuples_list:
            row_id, row_data = row[0], row[1]

            # get company hash
            company_hash = hashlib.sha256((row_data[3] + row_data[4]).encode('utf-8')).hexdigest()

            # if the company doesnt exist yet, process it
            if  company_hash not in self.added_companies_lst:
                errors, company_dic = company_validator.process_company(row_data)
            
                # if there are no errors add the company to json
                if len(errors) == 0:
                    self.add_company(company_dic, company_hash)
                    self.google_sheet.check_cell(row=row_id+1, col=self.validated_checkbox_column)
                # else print errors
                else:
                    print("[Company WAS NOT added to database] {} - {} | Errors={}".format(row_data[3],row_data[4], errors))  
                    self.google_sheet.uncheck_cell(row=row_id+1, col=self.validated_checkbox_column)

                # write errors to google sheets
                self.google_sheet.write_error(error=str(errors), row=row_id+1, col=self.error_col)

            else:
                print("[Company already in database] {} - {}".format(row_data[3],row_data[4])) 



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
            else:
                f_json_in_memory = {company_hash:company_dic}
                print("[Adding new company in new county ({})] {} - {}".format(poss_filename, company_dic["parish"], company_dic["name"]))

            # parse to json
            f_json = json.dumps(f_json_in_memory, ensure_ascii=False).encode('utf8').decode("utf8")
            # write the data
            f = open(Path(output_data[0], poss_filename), 'w')
            f.write(f_json)
            f.close()

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
        return files


    """
    Gets a list of all the companies that are already in database
    """
    def get_added_companies_hashes(self):
        f = open(self.added_companies_filename)
        return [line.strip() for line in f]

from os import path, listdir
import csv
import json
import hashlib
from company_validator import CompanyValidator


class FormValidator:

    GEOHASH_COUNTY_BYTES = 4
    DATA_BASE_DIR = '../Data'    
    ADDED_COMPANIES_FILE_NAME = 'added_companies_hashes'
    COUNTIES_DIR = 'Counties'
    

    errors = []

    def processCsv(self, csv_path):
        # check if file exists
        if not path.exists(csv_path):
            self.errors.append("Couldn't obatain csv!")
            return self.errors
        
        # get the list of all the jsons already added
        self.listed_counties = self.get_added_counties_jsons_names()

        # get all the companies that have already been added (hash of the companies)
        self.added_companies_lst = self.get_added_compamies_hashes()

        # Create a company validator
        company_validator = CompanyValidator()

        # process file
        f = open(csv_path, 'r')
        # skip header
        f.readline()

        csv_reader = csv.reader(f)
        for row in csv_reader:
            # get company hash
            company_hash = hashlib.sha256((row[3] + row[4]).encode('utf-8')).hexdigest()

            # if the company doesnt exist yet, process it
            if  company_hash not in self.added_companies_lst:
                errors, company_dic = company_validator.process_company(row)
            
                # if there are no errors add the company to json
                if len(errors) == 0:
                    self.add_company(company_dic, company_hash)
                # else print errors
                else:
                    print("[Company WAS NOT added to database] {} - {} | Errors={}".format(row[3],row[4], errors))  

            else:
                print("[Company already in database] {} - {}".format(row[3],row[4])) 

        return


    def get_added_compamies_hashes(self):
        f = open("{}/{}".format(self.DATA_BASE_DIR, self.ADDED_COMPANIES_FILE_NAME))
        return [line.strip() for line in f]


    def add_company(self, company_dic, company_hash):
        geohash = company_dic["geo_hash"]
        county_geohash = geohash[:self.GEOHASH_COUNTY_BYTES]

        # if there is already a council json created with that hash
        
        poss_filename = "{}.json".format(county_geohash)
        if poss_filename in self.listed_counties:
            # read json to memory and append to it
            f = open("{}/{}/{}".format(self.DATA_BASE_DIR, self.COUNTIES_DIR, poss_filename))
            f_json_in_memory = json.loads(f.read())
            f_json_in_memory.append(company_dic)

            # parse to json and override file
            f_json = json.dumps(f_json_in_memory, ensure_ascii=False).encode('utf8').decode("utf8")
            f = open("{}/{}/{}".format(self.DATA_BASE_DIR, self.COUNTIES_DIR, poss_filename), "w")
            f.write(f_json)
            f.close()
            print("[New company in existant county ({})] {} - {}".format(county_geohash, company_dic["freguesia"], company_dic["nome"]))
        
        else:
            data = [company_dic]
            f_json = json.dumps(data, ensure_ascii=False).encode('utf8').decode("utf8")
            f = open("{}/{}/{}".format(self.DATA_BASE_DIR, self.COUNTIES_DIR, poss_filename), "w")
            f.write(f_json)
            f.close()
            print("[New company in new county ({})] {} - {}".format(county_geohash, company_dic["freguesia"], company_dic["nome"]))

        # add company hash to list of added companies
        f = open("{}/{}".format(self.DATA_BASE_DIR, self.ADDED_COMPANIES_FILE_NAME), "a")
        f.write(str(company_hash) + "\n")
        f.close()

        #add also to the list that is loaded to memory
        self.added_companies_lst.append(company_hash)
        
        return


    def get_added_counties_jsons_names(self):
        files = []
        for f in listdir("{}/{}".format(self.DATA_BASE_DIR, self.COUNTIES_DIR)):
            if path.isfile("{}/{}/{}".format(self.DATA_BASE_DIR, self.COUNTIES_DIR, f)):
                files.append(f)
        return files

fv = FormValidator()
fv.processCsv("teste_v3.csv")
import geohash
import requests
import re
import json
import csv
from constants import company_validation_constants

class CompanyValidator():

    hours_regex = r"[0-9]{1,2}:[0-9]{1,2}"
    email_regex = r".+@.+\..+"
    GDRIVE_DOWNLOAD_BASE_LINK = "https://drive.google.com/uc?export=download&id="
    IMGUR_UPLOAD_API_CAL = "https://api.imgur.com/3/upload"
    

    def process_company(self, csv_list):
        # create errors array
        self.errors = []
        # create dic to hold information
        self.company_dic = {}

        # bind the data
        if not self.data_bindings(csv_list): 
            return self.errors, self.company_dic 

        # validate fields and create company dic

        # add address
        self.add_valid_address()
        # add the complete address - no validation here!
        self.company_dic["address"] = self.complete_adress
        # get coordinates, geo hash and location 
        # if there is no gmaps url in the csv, the gmaps_url_to_coordinates() will get a valid url
        latitude, longitude = self.gmaps_url_to_coordinates()
        geo_hash = self.coordinates_to_geohash(latitude, longitude)
        self.company_dic["latitude"] = latitude
        self.company_dic["longitude"] = longitude
        self.company_dic["geo_hash"] = geo_hash
        self.company_dic["gmaps_url"] = self.gmaps_url
        # add social media
        self.add_valid_social_media()
        # add valid email
        self.add_valid_email()
        # add name
        self.company_dic["nome"] = self.company_name
        # add website
        self.add_valid_website()
        # add notes
        self.company_dic["notas"] = self.notes
        # add home delivery
        self.add_valid_home_delivery()
        # add cellphones
        self.company_dic["contactos"] = {"telemovel":self.contacts, "telefone":[]}
        # add home address - empty for now
        self.company_dic["morada"] = ""
        # add valid categories
        self.add_valid_categories()
        # add valid schedules
        self.add_valid_schedules()
        # add valid images
        self.add_valid_images()
        # add id - for now -1
        self.company_dic["id"] = -1

        return self.errors, self.company_dic 


    """
    Binds the csv information to class variables
    Is the csv changes, adapt the variables here
    """
    def data_bindings(self, csv_list):
        try:
            self.district = csv_list[1]
            self.county = csv_list[2]
            self.parish = csv_list[3]
            self.company_name = csv_list[4]
            self.categories = csv_list[5].replace('"', '').split(",")
            self.contacts = [csv_list[6], csv_list[7]]
            self.email = csv_list[8]
            self.complete_adress = csv_list[9]
            self.gmaps_url = csv_list[10]        
            self.image_url_drive = csv_list[11]
            self.home_delivery = csv_list[12]
            self.notes = csv_list[13]
            self.facebook = csv_list[14]
            self.instagram = csv_list[15]
            self.twitter = csv_list[16]
            self.website = csv_list[17]
            self.schedules = [csv_list[18], csv_list[19], csv_list[20], csv_list[21], csv_list[22], csv_list[23], csv_list[24]]
            return True
        except:
            self.errors.append("Couldn't parse the csv line - list index out of range")
            return False


    """
    Checks if the website is valid, doing a request to validate the URL
    """
    def add_valid_website(self):
        if self.website.strip()=="":
            self.company_dic["website"] = ""
            return 

        try:
            website_url = requests.get(self.website).url
            self.company_dic["website"] = website_url
        except:
            self.errors.append("Invalid website!")


    """
    Checks if the companies email is ok
    """
    def add_valid_email(self):
        if self.email != '':
            try:
                if re.search(self.email_regex, self.email).group() != self.email: 
                    self.errors.append("Invalid email!")
            except:
                self.errors.append("Invalid email!")


            

    """
    Add the home delivery boolean to the company
    """
    def add_valid_home_delivery(self):
        if self.home_delivery.lower() == "sim":
            self.company_dic["entrega_em_casa"] = True
        else:
            self.company_dic["entrega_em_casa"] = False


    """
    Adds the valid social media to a dictionary <social_media : url>
    """
    def add_valid_social_media(self):
        if not ('facebook' in self.facebook.lower() or self.facebook==''): 
            self.errors.append("Invalid facebook!")
        if not ('instagram' in self.instagram.lower() or self.instagram==""): 
            self.errors.append("Invalid instagram!")
        if not ('twitter' in self.twitter.lower() or self.twitter==""): 
            self.errors.append("Invalid twitter!")

        social_media = {}
        social_media["facebook"] = self.facebook
        social_media["instagram"] = self.instagram
        social_media["twitter"] = self.twitter
        self.company_dic["redes_sociais"] = social_media


    """
    Check if the given coordinates are inside portugal and produce the geohash
    """
    def coordinates_to_geohash(self, latitude, longitude, precision=7):
        # check if coordinates in portugal
        if not (36.839377 < latitude < 42.117961):
             self.errors.append("Latitude is outside Portugal!")
        if not ( -10.170561 < longitude < -5.699126):
            self.errors.append("Longitude is outside Portugal!")

        return geohash.encode(latitude, longitude)


    """
    Check if the company contains a google maps location and traslates this location to coordinates
    If there is no gmaps url, use the google api to get a location url, given the complete address
    """
    def gmaps_url_to_coordinates(self):
        # if no location url
        if self.gmaps_url == '':
            self.get_gmaps_url_from_address()
        try:
            # if the link is a shorten one, we need to get the longer version
            complete_url = requests.get(self.gmaps_url).url
            splitted_url = complete_url.strip().split("@")[1].split(",")
            latitude = splitted_url[0]
            longitude = splitted_url[1]
            return float(latitude), float(longitude)
        except:
            self.errors.append("Couldn't decode gmaps url")
            return -1, -1

    

    """
    Get the google maps url to a certain location, given the addres of the company
    """
    # TODO -> inserir codigo do mendes aqui!
    def get_gmaps_url_from_address(self):
        self.gmaps_url = 'https://goo.gl/maps/XYpxDQhaZwMhFcd37'
        

    """
    Verifies the district, county and parish 
    """
    def add_valid_address(self):
        if self.district not in company_validation_constants.valid_districts:  
            self.errors.append("Invalid district!")
        if self.county not in company_validation_constants.valid_counties_by_district[self.district]: 
            self.errors.append("Invalid county or outside the district")
        if self.parish not in company_validation_constants.valid_parishes_by_county[self.county]: 
            self.errors.append("Invalid parish!")

        self.company_dic["distrito"] = self.district
        self.company_dic["concelho"] = self.county
        self.company_dic["freguesia"] = self.parish


    """
    Adds the valid schedules
    """
    def add_valid_schedules(self):
        if len(self.schedules) != 7:
            self.errors.append("Invalid number of days in schedule!")
        
        self.company_dic["horarios"] = {}

        try:
            for i in range(0,7):
                day, schedule = self.get_valid_schedule_for_day(company_validation_constants.valid_weekdays[i], self.schedules[i])
                self.company_dic["horarios"][day] = schedule
        except:
            self.errors.append("Error parsing schedules!")


    """ 
    Verifies if some schedule, for a given date is ok
    A schedule can be a set of hours, or ENCERRADO
    """
    def get_valid_schedule_for_day(self, day, schedules):
        try:
            # error threatment
            if day not in company_validation_constants.valid_weekdays: 
                self.errors.append("Invalid week day for {}!".format(day))

            # if no schedule for the day
            if schedules.strip() == "":
                return day, ["Sem Informação"]
            
            # if company is closed
            if schedules.strip().lower() == "encerrado":
                return day, ["Encerrado"]

            # list of schedules for the given day
            schedules_verified = []
            # get multiple schedules for a day
            for schedule in schedules.split(","):
                # remove multiple white spaces and strip
                schedule = ' '.join(schedule.strip().split())
                start, end = schedule.split("-")
                start = start.strip()
                end = end.strip()

                # assert the data is valid
                if re.search(self.hours_regex, start).group() != start: 
                    self.errors.append("Invalid starting hour for {}!".format(day))
                if re.search(self.hours_regex, end).group() != end:
                    self.errors.append("Invalid ending hour for {}!".format(day))

                # add to valid schedules
                schedules_verified.append("{} - {}".format(start, end))

            return day, schedules_verified
        except:
            self.errors.append("Invalid hours for for {}!".format(day))
            return 'None', ["None"]


    """
    Adds valid categories
    """
    def add_valid_categories(self):
        self.company_dic["categorias"] = []
        # assert each category is valid
        for cat in self.categories:
            cat = cat.strip()
            if cat not in company_validation_constants.valid_categories:
                self.errors.append("Invalid category for {}!".format(cat))
            else:
                # exception for saúde
                if cat == "Saúde (Clínica de Saúde,  Centro Saúde,  Dentista,  entre outros)":
                    cat = "Saúde"
                self.company_dic["categorias"].append(cat)
    
    
    """
    Adds an image to a company
    If there is an image to this company, it is hosted on googel drive
    This function downloads the image, in bytes, from the gdrive and uses the imgur api
    to upload it. Then the image will be nothing more than a link to the imgur
    """
    def add_valid_images(self):
        # if the company has no imgage
        if self.image_url_drive.strip() == '':
            self.company_dic["imagens"] = {"logotipo":"", "foto_exterior":""}
            return

        # if link is incorrect
        if "drive.google.com" not in self.image_url_drive:
            self.errors.append("Ivalid url for image")
            return

        # get the image from the google drive
        m_bytes = bytes()
        try:
             # get the image id
            img_id = self.image_url_drive.strip().split("id=")[1]  
            # get bytes from the image
            r = requests.get("{}{}".format(self.GDRIVE_DOWNLOAD_BASE_LINK, img_id), stream=True)
            if r.status_code == 200:
                for chunk in r:
                    m_bytes += (chunk)
        except Exception as e: 
            self.errors.append("unable to download image - {}!".format(e))
        
        # post the image on imgur
        try:
            data = {"image": m_bytes, "type":"file", "name":self.company_name}
            headers = {'Authorization': 'Client-ID 9d7c6d95294614e'}
            r = requests.post(self.IMGUR_UPLOAD_API_CAL, data = data, headers=headers)
            # if upload resulted in an error
            if "error" in r.json()["data"]:
                self.errors.append("Error on uploading image to imgur - {}!".format(r.json()["data"]["error"]))
            # if all ok
            imgur_link_to_img = r.json()["data"]["link"]
            self.company_dic["imagens"] = {"logotipo":imgur_link_to_img, "foto_exterior":""}
        except:
            self.errors.append("unable to upload image to imgur!")
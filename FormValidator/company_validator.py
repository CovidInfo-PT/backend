import geohash
import requests
import re
import json
import csv
from constants import company_validation_constants

class CompanyValidator():

    hours_regex = r"[0-9]{1,2}:[0-9]{1,2}"
    GDRIVE_DOWNLOAD_BASE_LINK = "https://drive.google.com/uc?export=download&id="
    IMGUR_UPLOAD_API_CAL = "https://api.imgur.com/3/upload"
    

    def process_company(self, csv_list):
        # create errors array
        self.errors = []
        # create dic to hold information
        self.company_dic = {}

        self.district = csv_list[1]
        self.county = csv_list[2]
        self.parish = csv_list[3]
        self.company_name = csv_list[4]
        self.contacts = [csv_list[5], csv_list[6]]
        self.gmaps_url = csv_list[7]
        self.categories = csv_list[8].replace('"', '').split(",")
        self.image_url_drive = csv_list[9]
        self.home_delivery = csv_list[10]
        self.notes = csv_list[11]
        self.facebook = csv_list[12]
        self.instagram = csv_list[13]
        self.twitter = csv_list[14]
        self.website = csv_list[15]
        self.schedules = [csv_list[16], csv_list[17], csv_list[18], csv_list[19], csv_list[20], csv_list[21], csv_list[22]]

        # validate fields and create company dic
        # add address
        self.add_valid_address()
        # get coordinates, geo hash and location
        latitude, longitude = self.gmaps_url_to_coordinates()
        geo_hash = self.coordinates_to_geohash(latitude, longitude)
        self.company_dic["latitude"] = latitude
        self.company_dic["longitude"] = longitude
        self.company_dic["geo_hash"] = geo_hash
        self.company_dic["gmaps_url"] = self.gmaps_url
        # add social media
        self.add_valid_social_media()
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


    def add_valid_website(self):
        if self.website.strip()=="":
            self.company_dic["website"] = ""
            return 

        try:
            website_url = requests.get(self.website).url
            self.company_dic["website"] = website_url
        except:
            self.errors.append("Invalid website!")


    # VERIFICAR
    def add_valid_home_delivery(self):
        if self.home_delivery.lower() == "sim":
            self.company_dic["entrega_em_casa"] = True
        else:
            self.company_dic["entrega_em_casa"] = False


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


    def coordinates_to_geohash(self, latitude, longitude, precision=7):
        # check if coordinates in portugal
        if not (36.839377 < latitude < 42.117961):
             self.errors.append("Latitude is outside Portugal!")
        if not ( -10.170561 < longitude < -5.699126):
            self.errors.append("Longitude is outside Portugal!")

        return geohash.encode(latitude, longitude)


    def gmaps_url_to_coordinates(self):
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


    def get_valid_schedule_for_day(self, day, schedules):
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
        for schedule in schedules.split("|"):
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


    def add_valid_categories(self):
        self.company_dic["categorias"] = []
        # assert each category is valid
        for cat in self.categories:
            cat = cat.strip()
            if cat not in company_validation_constants.valid_categories:
                self.errors.append("Invalid category for {}!".format(cat))
            else:
                self.company_dic["categorias"].append(cat)
    
    
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



'''
# Testings

fv = CompanyValidator()
#print(fv.gmaps_url_to_coordinates("https://goo.gl/maps/VxidNVxVknbuXCN69") == (40.2514534,-8.4322546))
#print(fv.get_valid_schedule("segunda-feira", "10:00 - 13:00 | 15:00 - 20:00") == ("segunda-feira", ["10:00 - 13:00", "15:00 - 20:00"]))
#fv.assert_address("Aveiro", "Mealhada", "Pampilhosa")


line = "4/3/2020 12:49:52,Viseu,Carregal do Sal,Currelos,Minimercado Celestina,963167335,232961077,https://goo.gl/maps/NEZ53Y5JMVNWMRk96,Mercados,https://drive.google.com/open?id=1SOJgeQmX0auKw_ig3sH9DeeGBrYFSIGP,,,https://www.facebook.com/Minimercado-Celestina-102352701186715/,,,,09:30 - 12:30 | 15:30 - 18h30,09:30 - 12:30 | 15:30 - 18h30,09:30 - 12:30 | 15:30 - 18h30,09:30 - 12:30 | 15:30 - 18h30,09:30 - 12:30 | 15:30 - 18h30,09:30 - 12:30 ,ENCERRADO"
line_ok = "4/3/2020 12:49:52,Viseu,Carregal do Sal,Carregal do Sal,Minimercado Celestina,963167335,232961077,https://goo.gl/maps/NEZ53Y5JMVNWMRk96,Mercados,https://drive.google.com/open?id=1SOJgeQmX0auKw_ig3sH9DeeGBrYFSIGP,,,https://www.facebook.com/Minimercado-Celestina-102352701186715/,,,,09:30 - 12:30 | 15:30 - 18:30,09:30 - 12:30 | 15:30 - 18:30,09:30 - 12:30 | 15:30 - 18:30,09:30 - 12:30 | 15:30 - 18:30,09:30 - 12:30 | 15:30 - 18:30,,ENCERRADO"

errors, di = fv.process_company(line_ok)
print(errors)
print(di)
'''
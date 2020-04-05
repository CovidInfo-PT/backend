import json
import requests
import geohash


def county_to_geohash(county, district):
    query = "{},{},Portugal".format(county, district)
    info = requests.get("https://nominatim.openstreetmap.org/search?q={}&format=json".format(query)).json()  
    if len(info) == 0:
        print("Couldn't find {}".format(query)) 
        return "-1" 
    latitude = float(info[0]["lat"])
    longitude = float(info[0]["lon"])
    return geohash.encode(latitude, longitude)

f = open("datasets/freguesias-metadata.csv")

# ignore header
f.readline()

parishes_by_county = {}
counties_by_district = {}

parishes = set()
counties = set()
districts = set()

for line in f:
    splitted_line = line.split(";")
    district, county, parish = splitted_line[1], splitted_line[2], splitted_line[3]
    districts.add(district)
    counties.add(county)
    parishes.add(parish)
    
    # parishes by counties
    if county in parishes_by_county:
        parishes_by_county[county].add(parish)
    else:
        parishes_by_county[county] = set([parish])

    # counties by district
    if district in counties_by_district:
        counties_by_district[district].add(county)
    else:
        counties_by_district[district] = set([county])



# generate geohashes for each county
counties_by_district_geohashed ={}
for d in counties_by_district:
    
    counties_by_district_geohashed[d] = [[c, county_to_geohash(c, d)] for c in counties_by_district[d]]
    print(d)


print(counties_by_district_geohashed)


# convert sets to lists to dump to json files
for d in counties_by_district:
    counties_by_district[d] = sorted(list(counties_by_district[d]))

for c in parishes_by_county:
    parishes_by_county[c] = sorted(list(parishes_by_county[c]))

# to json
counties_by_district_json = json.dumps(counties_by_district, ensure_ascii=False).encode('utf8').decode("utf8")
parishes_by_county_json = json.dumps(parishes_by_county, ensure_ascii=False).encode('utf8').decode("utf8")
counties_by_district_geohashed_json = json.dumps(counties_by_district_geohashed, ensure_ascii=False).encode('utf8').decode("utf8")
parishes_json = json.dumps(list(parishes), ensure_ascii=False).encode('utf8').decode("utf8")
counties_json = json.dumps(list(counties), ensure_ascii=False).encode('utf8').decode("utf8")
districts_json = json.dumps(list(districts), ensure_ascii=False).encode('utf8').decode("utf8")


# save to files
counties_by_district_file = open("outputs/counties_by_district.json", "w")
counties_by_district_file.write(counties_by_district_json)
counties_by_district_file.close()

counties_by_district_geohashed_file = open("outputs/counties_by_district_geohashed_not_completed.json", "w")
counties_by_district_geohashed_file.write(counties_by_district_geohashed_json)  
counties_by_district_geohashed_file.close()

parishes_by_county_file = open("outputs/parishes_by_county.json", "w")
parishes_by_county_file.write(parishes_by_county_json)
parishes_by_county_file.close()

districts_file = open("outputs/districts.json", "w")
districts_file.write(districts_json)
districts_file.close()

counties_file = open("outputs/counties.json", "w")
counties_file.write(counties_json)
counties_file.close()

parishes_file = open("outputs/parishes.json", "w")
parishes_file.write(districts_json)
parishes_file.close()









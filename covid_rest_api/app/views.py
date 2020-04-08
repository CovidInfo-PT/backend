from django.shortcuts import render
import json

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
)


# 'method' can be used to customize a single HTTP method of a view
@api_view(["GET"])
def all_districts(request):
    try:
        # open the file
        districts_file = open('static/auxiliar/districts.json', 'r')
        districts = json.loads(districts_file.read())
        return Response({"state":"success", "districts": districts}, status=HTTP_200_OK)

    except Exception as e:
        return Response({"state": "error", "error": e}, status=HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def all_counties(request):
    try:
        # open the file
        counties_file = open('static/auxiliar/counties_by_district_geohashed.json', 'r')
        counties = json.loads(counties_file.read())
        return Response({"state":"success", "counties": counties}, status=HTTP_200_OK)

    except Exception as e:
        return Response({"state": "error", "error": e}, status=HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def counties_by_distric(request):

    param_keys = request.GET.keys()

    # validating parameters
    if 'district' not in param_keys:
        return Response({"state": "error", "error": "you must send a district"}, status=HTTP_400_BAD_REQUEST)

    # get district
    district = request.GET['district']

    try:
        # open the file
        counties_file = open('static/auxiliar/counties_by_district_geohashed.json', 'r')
        counties = json.loads(counties_file.read())

        elected_counties = []
        if district in counties:
            elected_counties = counties[district]

        return Response({"state":"success", "district":district, "counties": elected_counties}, status=HTTP_200_OK)

    except Exception as e:
        return Response({"state": "error", "error": e}, status=HTTP_200_OK)



def companies_by_county(county, county_geohash=None):
    
    try:
        f = open(f'static/emulated_database/companies_by_location/by_name/{county}.json', 'r')
        companies_by_name = json.loads(f.read())
    except Exception as e:
        companies_by_name = {}

    if county_geohash is None:
        try:
            f = open('static/auxiliar/counties_geohashes.json', 'r')
            geohashes = json.loads(f.read())
            county_geohash = geohashes[county]
        except Exception as e:
            return

    try: 
        f = open(f'static/emulated_database/companies_by_location/by_geohash/{county_geohash[:4]}.json', 'r')
        companies_by_geohash = json.loads(f.read())
    except Exception as e:
        companies_by_geohash = {}
    
    all_companies = {company:companies_by_name[company] for company in companies_by_name}
    for company in companies_by_geohash:
        all_companies[company] = companies_by_geohash[company]
    
    return all_companies

@api_view(["GET"])
def companies_by_location(request):

    param_keys = request.GET.keys()
    

    if 'county' in param_keys:
        
        try:
            county = request.GET['county']

            all_companies = companies_by_county(county)
            
            if all_companies is not None:
                return Response({"state": "success", "county": county, "companies": all_companies}, status=HTTP_200_OK)

            return Response({"state": "error", "county": "County not found!"})

        except Exception as e:
            return Response({"state": "error", "county": "County not found!"})

    elif 'district' in param_keys:

        try: 
            district = request.GET['district']
            
            f = open(f'static/auxiliar/counties_by_district_geohashed.json', 'r')
            districts = json.loads(f.read())

            all_companies = {}

            for county in districts[district]:
                county_companies = companies_by_county(county[0], county[1])
                all_companies.update(county_companies)

            return Response({"state": "success", "district": district, "companies": all_companies}, status=HTTP_200_OK)
            
        except Exception as e:
            return Response({"state": "error", "error": "District not found!"}, status=HTTP_200_OK)
    
    elif 'geohash' in param_keys:

        try:
            geohash = request.GET['geohash']
            
            f = open('static/auxiliar/geohashes.json', 'r')
            geohashes = json.loads(f.read())
            
            county = geohashes[geohash]['county']
            all_companies = companies_by_county(county, geohash)
            
            return Response({"state": "success", "county": county, "companies": all_companies}, status=HTTP_200_OK)

        except Exception as e:
            return Response({"state": "error", "error": "Geohash not found!"}, status=HTTP_200_OK)
    
    else:
        return Response({"state": "error", "error": "You must provide a district, a county or a geohash!"}, status=HTTP_200_OK)

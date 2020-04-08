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




@api_view(["GET"])
def companies_by_location(request):

    param_keys = request.GET.keys()
    

    if 'county' in param_keys:

        county = request.GET['county']

        f = open(f'static/companies_by_location/by_name/{county}.json', 'r')
        companies_by_name = json.loads(f.read())

        f = open('static/auxiliar/counties_geohashes.json', 'r')
        geohashes = json.loads(f.read())
        county_geohash = geohashes[county]

        f = open(f'static/companies_by_location/by_geohash/{county_geohash[:4]}.json', 'r')
        companies_by_geohash = json.loads(f.read())


        all_companies = {company:companies_by_name[company] for company in companies_by_name}
        for company in companies_by_geohash:
            all_companies[company] = companies_by_geohash[company]

        return Response({"state": "success", "county": county, "companies": all_companies})



            
"""
    # validating parameters
    if 'geohash' not in param_keys:
        return Response({"state": "error", "error": "you must send a geohash"}, status=HTTP_400_BAD_REQUEST)

    # get geohash
    geohash = request.GET['geohash']

    try:
        # open the file
        companies_by_location = open('static/companies_by_counties/ez4m.json', 'r')
        companies_by_location = json.loads(companies_by_location.read())

        return Response({"state":"success",  "location": geohash, "companies":companies_by_location}, status=HTTP_200_OK)

    except Exception as e:
        return Response({"state": "error", "error": e}, status=HTTP_200_OK)


@api_view(["GET"])
def companies_by_location_name(request):

    param_keys = request.GET.keys()
    
    # validating parameters
    if 'district' not in param_keys and 'county' not in param_keys:
        return Response({"state": "error", "error": "you must send a district or county name!"}, status=HTTP_400_BAD_REQUEST)

    county = request.GET['location']

    try:
        companies = open(f'static/counties/by_name/{county}.json', 'r')
        companies = json.loads(companies.read())

        return Response({"state": "success", "data": companies}, status=HTTP_200_OK)
    
    except Exception as e:
        return Response({"state": "error", "error": "Location not found!"}, status=HTTP_200_OK)

"""
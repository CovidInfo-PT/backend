from django.shortcuts import render
import json
from pathlib import Path
import os
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
)

from django.views.decorators.cache import cache_control


# OPEN ALL STATIC FILES IN MEMORY
with open('static/auxiliar/districts.json', 'r') as f:
    districts = json.loads(f.read())

with open('static/auxiliar/counties_by_district_geohashed.json', 'r') as f:
    counties = json.loads(f.read())

with open('static/auxiliar/counties_geohashes.json', 'r') as f:
    counties_geohashes = json.loads(f.read())

with open('static/auxiliar/geohashes.json', 'r') as f:
    geohashes = json.loads(f.read())


# CHECK IF EMULATED DATABASE IS IN OTHER DIR
tmp_db_dir = os.getenv('EMULATED_DATABASE_DIR')


EMULATED_DATABASE_DIR = tmp_db_dir if (tmp_db_dir != None and os.path.isdir(tmp_db_dir)) else 'static/emulated_database/'
print(f'Will be using the emulated database at {EMULATED_DATABASE_DIR} !')


# CACHE-CONTROL SETTINGS
CACHE_CONTROL = {
    'public': True,
    #  HOURS * MINUTES * SECONDS
    'max_age': 12*60*60, 
    's_maxage': 12*60*60
}


# 'method' can be used to customize a single HTTP method of a view
@api_view(["GET"])
@cache_control(public=CACHE_CONTROL['public'],  max_age=CACHE_CONTROL['max_age'], s_maxage=CACHE_CONTROL['s_maxage'])
def all_districts(request):
    try:
        return Response({"state":"success", "districts": districts}, status=HTTP_200_OK)

    except Exception as e:
        return Response({"state": "error", "error": e}, status=HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@cache_control(public=CACHE_CONTROL['public'],  max_age=CACHE_CONTROL['max_age'], s_maxage=CACHE_CONTROL['s_maxage'])
def all_counties(request):
    try:
        return Response({"state":"success", "counties": counties}, status=HTTP_200_OK, )

    except Exception as e:
        return Response({"state": "error", "error": e}, status=HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@cache_control(public=CACHE_CONTROL['public'],  max_age=CACHE_CONTROL['max_age'], s_maxage=CACHE_CONTROL['s_maxage'])
def counties_by_distric(request):

    param_keys = request.GET.keys()

    # validating parameters
    if 'district' not in param_keys:
        return Response({"state": "error", "error": "you must send a district"}, status=HTTP_400_BAD_REQUEST)

    # get district
    district = request.GET['district']

    try:

        elected_counties = []
        if district in counties:
            elected_counties = counties[district]

        return Response({"state":"success", "district":district, "counties": elected_counties}, status=HTTP_200_OK)

    except Exception as e:
        return Response({"state": "error", "error": e}, status=HTTP_200_OK)



def companies_by_county(county, county_geohash=None):
    
    try:
        f = open(Path(EMULATED_DATABASE_DIR, f'companies_by_location/by_name/{county}.json'), 'r')
        companies_by_name = json.loads(f.read())
    except Exception as e:
        companies_by_name = {}

    if county_geohash is None:
        try:
            county_geohash = counties_geohashes[county]
        except Exception as e:
            return

    try: 
        f = open(Path(EMULATED_DATABASE_DIR, f'companies_by_location/by_geohash/{county_geohash[:4]}.json') , 'r')
        companies_by_geohash = json.loads(f.read())
    except Exception as e:
        companies_by_geohash = {}
    
    all_companies = {company:companies_by_name[company] for company in companies_by_name}
    for company in companies_by_geohash:
        all_companies[company] = companies_by_geohash[company]
    
    return all_companies

@api_view(["GET"])
@cache_control(public=CACHE_CONTROL['public'],  max_age=CACHE_CONTROL['max_age'], s_maxage=CACHE_CONTROL['s_maxage'])
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
            
            districts = counties

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
            
            county = geohashes[geohash]['county']
            all_companies = companies_by_county(county, geohash)
            
            return Response({"state": "success", "county": county, "companies": all_companies}, status=HTTP_200_OK)

        except Exception as e:
            return Response({"state": "error", "error": "Geohash not found!"}, status=HTTP_200_OK)
    
    else:
        return Response({"state": "error", "error": "You must provide a district, a county or a geohash!"}, status=HTTP_200_OK)


@api_view(["GET"])
@cache_control(public=CACHE_CONTROL['public'],  max_age=CACHE_CONTROL['max_age'], s_maxage=CACHE_CONTROL['s_maxage'])
def categories(request):

    # in memory to avoid disk access
    categories = sorted(['Lavandaria', 'Café','Correio', 'Saúde', 'Farmácias', 'Restaurantes', 'Mercados', 'Padarias', 'Talhos', 'Peixarias', 'Bombas de Combustível', 'Gás', 'Oficinas', 'Bancos', 'Serviços Administrativos', 'Telecomunicações', 'Veterinários', 'Recolha de Lixo'])
    categories.append('Outros')

    return Response({"state": "success", "categories": categories}, status=HTTP_200_OK)


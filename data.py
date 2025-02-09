# Script containing useful data functions
# Main data script for extracting data from US open data
# Data found at https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/about_data

# Data and math management libraries
import pandas as pd
import numpy as np

# Open data API library 
from sodapy import Socrata

import config

# Calls the API based on a list of parameters, returns the result as a pandas df
def call_api(query):
    client = Socrata("data.cityofnewyork.us",
                    config.token,
                    username=config.username,
                    password=config.password)

    results = client.get("43nn-pn8j", query=query)

    return pd.DataFrame.from_records(results)


# Query based on the restaurant zipcode
def query_zipcode(zipcode, limit=20):
    return (
        f'select distinct dba '
        f'where zipcode = \'{zipcode}\' \n'
        f'limit {limit}'
    )
    

# Query based on world coordinates, coord_range determines the max distance to check for restaurants from lat and lon
def query_coords(latitude, longitude, coord_range=0.02, limit=15):
    return (
        f'select distinct dba \n' 
        f'where latitude > {latitude - coord_range} and latitude < {latitude + coord_range} \n'
        f'        and longitude > {longitude - coord_range} and longitude < {longitude + coord_range} \n'
        f'limit {limit}'        
    )
                            

# interface for query and calling the api
def get_data(**query_args):
    
    # query based on zipcode
    '''
    *can we make the lat and lon a pair instead of seperate variables*
    '''
    if 'zipcode' in query_args and 'latitude' not in query_args and 'longitude' not in query_args:
        query = query_zipcode(zipcode=query_args['zipcode'], limit=query_args['limit'])
        return call_api(query)
    
    # query based on coordinates
    elif 'latitude' in query_args and 'longitude' in query_args and 'zipcode' not in query_args:
        query = query_coords(latitude=query_args['latitude'], longitude=query_args['longitude'], coord_range=query_args['coord_range'], limit=query_args['limit'])
        return call_api(query)
    
    # if the parameters do not match, raise an exception
    else:
        if 'zipcode' in query_args or 'latitude' in query_args or 'longitude' in query_args:
            raise Exception('\nThe parameters you input clash, please choose zipcode or coordinates, not both.\n')
        else:
            raise Exception('\nThe parameters you input do not match any of the available queries, try zipcode or coordinates.\n')
    
    
        

    
    
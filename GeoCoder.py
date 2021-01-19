# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 18:33:27 2020

@author: Zitong Yashar
"""
import pandas as pd
import numpy as np
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle
import os
import sys
from geopy.geocoders import GoogleV3
import censusgeocode as cg
import time
    
### setiing up google geolocater ###
api_key = '' #####Put your API key here
geolocator = GoogleV3(api_key = api_key, timeout=None)

# Google_geocoder_address is a class that sends request (address components) to google geocoder api
# and gets the response and parse it (tries is the number of retries to send request and
# get response each retry has 3 seconds delay. This is to prevent temporary internet problem)

class Google_geocoder_address:
    def __init__ (self, gps_id, street = None, city = None, state = None, postal_code = None, country = "US", one_line_address = None, tries = 5):
        components = {}
        for component in ["city", "state", "postal_code", "country"]:
            if eval(component):
                components[component] = eval(component)
        if one_line_address:
            street = one_line_address
            
        for _ in range(tries):
            try:
                self.google_response = geolocator.geocode(str(street),
                                                          components = components,
                                                          language = 'en') 
            except Exception as e:
                if _ < tries - 1: # _ is zero indexed
                    time.sleep(3)
                    continue
                else:
                    print(e)
                    pass
                
        if self.google_response is None:
            if "postal_code" in components:
                components = {"postal_code" : postal_code}
                for _ in range(tries):
                    try:
                        self.google_response = geolocator.geocode(str(street),
                                                                  components = components,
                                                                  language = 'en')
                        
                    except Exception as e:
                        if _ < tries - 1: # _ is zero indexed
                            time.sleep(3)
                            continue
                        else:
                            print(e)
                            pass
            else:
                for _ in range(tries):
                    try:
                        self.google_response = geolocator.geocode(str(street),
                                                          language = 'en')
                        
                    except Exception as e:
                        if _ < tries - 1: # _ is zero indexed
                            time.sleep(3)
                            continue
                        else:
                            print(e)
                            pass
                    
        street_number_index = route_index = city_index = county_index = state_index = country_index = zip_code_index = zip_code_suffix_index = None
        self.lat = ''
        self.long = ''
        self.county = ''
        self.one_line_address = ''
        if self.google_response is not None:
            #getting the index for address components
            for address_component_index in range(len(self.google_response.raw['address_components'])):
                if self.google_response.raw['address_components'][address_component_index]['types'][0] == 'street_number':
                    street_number_index = address_component_index
                if self.google_response.raw['address_components'][address_component_index]['types'][0] == 'route':
                    route_index = address_component_index
                if self.google_response.raw['address_components'][address_component_index]['types'][0] == 'locality':
                    city_index = address_component_index
                if self.google_response.raw['address_components'][address_component_index]['types'][0] == 'administrative_area_level_2':
                    county_index = address_component_index
                if self.google_response.raw['address_components'][address_component_index]['types'][0] == 'administrative_area_level_1':
                    state_index = address_component_index
                if self.google_response.raw['address_components'][address_component_index]['types'][0] == 'country':
                    country_index = address_component_index
                if self.google_response.raw['address_components'][address_component_index]['types'][0] == 'postal_code':
                    zip_code_index = address_component_index
                if self.google_response.raw['address_components'][address_component_index]['types'][0] == 'postal_code_suffix':
                    zip_code_suffix_index = address_component_index
            print("Get response.")
            self.lat = self.google_response.latitude
            self.long = self.google_response.longitude
            self.one_line_address = self.google_response.address
        
   
        #adding info of location_info_from_google dataframe from google response
        if street_number_index == None:
            self.standard_address_street_number_long = ''
            self.standard_address_street_number_short = ''
        else:
            self.standard_address_street_number_long = self.google_response.raw['address_components'][street_number_index]['long_name']
            self.standard_address_street_number_short = self.google_response.raw['address_components'][street_number_index]['short_name']
        
        if route_index == None:
             self.standard_address_route_long = ''
             self.standard_address_route_short = ''
        else:
             self.standard_address_route_long =  self.google_response.raw['address_components'][route_index]['long_name']
             self.standard_address_route_short =  self.google_response.raw['address_components'][route_index]['short_name']
        
        if city_index == None:
             self.standard_address_city_long = ''
             self.standard_address_city_short = ''
        else:
             self.standard_address_city_long =  self.google_response.raw['address_components'][city_index]['long_name']
             self.standard_address_city_short =  self.google_response.raw['address_components'][city_index]['short_name']
        
        if county_index == None:
             self.standard_address_county_long = ''
             self.standard_address_county_short = ''
        else:
             self.standard_address_county_long =  self.google_response.raw['address_components'][county_index]['long_name']
             self.standard_address_county_short =  self.google_response.raw['address_components'][county_index]['short_name']
            
        if state_index == None:
             self.standard_address_state_long = ''
             self.standard_address_state_short = ''
        else:
             self.standard_address_state_long = self.google_response.raw['address_components'][state_index]['long_name']
             self.standard_address_state_short =  self.google_response.raw['address_components'][state_index]['short_name']
        
        if country_index == None:
             self.standard_address_country_long = ''
             self.standard_address_country_short = ''
        else:
             self.standard_address_country_long =  self.google_response.raw['address_components'][country_index]['long_name']
             self.standard_address_country_short =  self.google_response.raw['address_components'][country_index]['short_name']
        
        if zip_code_index == None:
             self.standard_address_zip_code_long = ''
             self.standard_address_zip_code_short = ''
        else:
             self.standard_address_zip_code_long =  self.google_response.raw['address_components'][zip_code_index]['long_name']
             self.standard_address_zip_code_short =  self.google_response.raw['address_components'][zip_code_index]['short_name']
        
        if zip_code_suffix_index == None:
             self.standard_address_zip_code_suffix_long = ''
             self.standard_address_zip_code_suffix_short = ''
        else:
             self.standard_address_zip_code_suffix_long =  self.google_response.raw['address_components'][zip_code_suffix_index]['long_name']
             self.standard_address_zip_code_suffix_short =  self.google_response.raw['address_components'][zip_code_suffix_index]['short_name']


# Census_geocoder_coordinate is class that sends request (coordinates) to census api
# and gets the response and parse it (tries is the number of retries to send request and
# get response each retry has 3 seconds delay. This is to prevent temporary internet problem)
class Census_geocoder_coordinate:
    def __init__ (self, gps_id, long, lat, tries = 5):
        for _ in range(tries):
            try:
                self.census_response = cg.coordinates(x = long,
                                                      y = lat)
                
            except Exception as e:
                if _ < tries - 1: # _ is zero indexed
                    time.sleep(3)
                    continue
                else:
                    print(e)
                    pass
        
        #adding info of location_info_from_census dataframe from google response
        try:
            self.long = long
            self.lat = lat
            self.block_group = self.census_response['2020 Census Blocks'][0]['BLKGRP']
            self.block = self.census_response['2020 Census Blocks'][0]['BLOCK']
            self.county = self.census_response['2020 Census Blocks'][0]['COUNTY']
            self.geo_id = self.census_response['2020 Census Blocks'][0]['GEOID']
            self.object_id = self.census_response['2020 Census Blocks'][0]['OID']
            self.state = self.census_response['2020 Census Blocks'][0]['STATE']
            self.tract = self.census_response['2020 Census Blocks'][0]['TRACT']
        except Exception as e:
            self.long = np.nan
            self.lat = np.nan
            self.block_group = np.nan
            self.block = np.nan
            self.county = np.nan
            self.geo_id = np.nan
            self.object_id = np.nan
            self.state = np.nan
            self.tract = np.nan
            print ('on gps_id: ', gps_id, "\n", e)

    





#xl = pd.ExcelFile('E:/COVID2020/Testdata_cleaning/NBSforcoding_121120.xlsx')
#dataframe = xl.parse("PCRRES")

# Extract data from the excel file
xl = pd.ExcelFile('E:/COVID2020/Testdata_cleaning/Lab Testing Data/LabTesting Data20210104121802/NBSforcoding.xlsx')
dataframe = xl.parse("1211")

dataframe.to_csv('E:/COVID2020/temp.csv' , index = False, encoding = "utf-8")

df = pd.read_csv('E:/COVID2020/temp.csv', header = 0, dtype={'PAT_ZIP_CODE': 'str'}, low_memory = False, encoding= 'unicode_escape')
print(len(df))
for row in range(len(df)): 
    address = f'{df.at[row,"PAT_ADDRESS_STREET_ONE"]}, '\
          f'{df.at[row,"PAT_ADDRESS_CITY"]}, '\
          f'{df.at[row,"PAT_STATE"]}'
    print("row ", row, ": ", address)
    zipcode = f'{df.at[row,"PAT_ZIP_CODE"]}'
    
# Generate latitude and longtitude 
    try:      
       google_geo = Google_geocoder_address (gps_id = row,
                                          postal_code = zipcode,
                                          one_line_address = address)
       latstring = google_geo.lat
       print("Geocoder executed.")
    except:
        latstring = ''
      
    try:
        df.at[row,"patient_lat"] = google_geo.lat
        df.at[row,"patient_long"] = google_geo.long
        df.at[row,"county"] = google_geo.standard_address_county_short
    except Exception:
        print("Unable to generate latitude at this line.")
    
# If latitude & longtitude can be generated from the address, generate state, county, block, tract info
    print(latstring)
    if latstring == '': 
        continue
    else:
        census_geo = Census_geocoder_coordinate (gps_id = row,
                                             long = google_geo.long,
                                             lat = google_geo.lat
                                             )
        df.at[row,"state #"] = census_geo.state
        df.at[row,"county #"] = census_geo.county
        df.at[row,"block #"] = census_geo.block
        df.at[row,"tract #"] = census_geo.tract
        

df.to_csv(r'E:\COVID2020\nbsgeocoder1211.csv')


          




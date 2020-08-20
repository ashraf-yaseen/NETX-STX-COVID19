# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 19:19:45 2019

@author: Yashar
"""
import pandas as pd
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle
import os
from geopy.geocoders import GoogleV3
import time
import sys
    
def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, -1)
    
def load_object(filename):
    with open(filename, 'rb') as input:
        return pickle.load(input)

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

# Google_geocoder_coordinate is a class that sends request (coordinates) to census api
# and gets the response and parse it (tries is the number of retries to send request and
# get response each retry has 3 seconds delay. This is to prevent temporary internet problem)
class Google_geocoder_coordinate:
    def __init__ (self, gps_id, long, lat, tries = 5):
        for _ in range(tries):
            try:
                self.google_response = geolocator.reverse(f'{lat}, {long}', exactly_one = False)
                
            except Exception as e:
                if _ < tries - 1: # _ is zero indexed
                    time.sleep(3)
                    continue
                else:
                    print(e)
                    pass
        street_number_index = route_index = city_index = county_index = state_index = country_index = zip_code_index = zip_code_suffix_index = None
        #getting the index for address components
        for address_component_index in range(len(self.google_response[0].raw['address_components'])):
            if self.google_response[0].raw['address_components'][address_component_index]['types'][0] == 'street_number':
                street_number_index = address_component_index
            if self.google_response[0].raw['address_components'][address_component_index]['types'][0] == 'route':
                route_index = address_component_index
            if self.google_response[0].raw['address_components'][address_component_index]['types'][0] == 'locality':
                city_index = address_component_index
            if self.google_response[0].raw['address_components'][address_component_index]['types'][0] == 'administrative_area_level_2':
                county_index = address_component_index
            if self.google_response[0].raw['address_components'][address_component_index]['types'][0] == 'administrative_area_level_1':
                state_index = address_component_index
            if self.google_response[0].raw['address_components'][address_component_index]['types'][0] == 'country':
                country_index = address_component_index
            if self.google_response[0].raw['address_components'][address_component_index]['types'][0] == 'postal_code':
                zip_code_index = address_component_index
            if self.google_response[0].raw['address_components'][address_component_index]['types'][0] == 'postal_code_suffix':
                zip_code_suffix_index = address_component_index
        
        
    
        #adding info of location_info_from_google dataframe from google response
        self.lat = self.google_response[0].latitude
        self.long = self.google_response[0].longitude
        self.one_line_address = self.google_response[0].address
    
        if street_number_index == None:
            self.standard_address_street_number_long = ''
            self.standard_address_street_number_short = ''
        else:
            self.standard_address_street_number_long = self.google_response[0].raw['address_components'][street_number_index]['long_name']
            self.standard_address_street_number_short = self.google_response[0].raw['address_components'][street_number_index]['short_name']
        
        if route_index == None:
             self.standard_address_route_long = ''
             self.standard_address_route_short = ''
        else:
             self.standard_address_route_long =  self.google_response[0].raw['address_components'][route_index]['long_name']
             self.standard_address_route_short =  self.google_response[0].raw['address_components'][route_index]['short_name']
        
        if city_index == None:
             self.standard_address_city_long = ''
             self.standard_address_city_short = ''
        else:
             self.standard_address_city_long =  self.google_response[0].raw['address_components'][city_index]['long_name']
             self.standard_address_city_short =  self.google_response[0].raw['address_components'][city_index]['short_name']
        
        if county_index == None:
             self.standard_address_county_long = ''
             self.standard_address_county_short = ''
        else:
             self.standard_address_county_long =  self.google_response[0].raw['address_components'][county_index]['long_name']
             self.standard_address_county_short =  self.google_response[0].raw['address_components'][county_index]['short_name']
            
        if state_index == None:
             self.standard_address_state_long = ''
             self.standard_address_state_short = ''
        else:
             self.standard_address_state_long = self.google_response[0].raw['address_components'][state_index]['long_name']
             self.standard_address_state_short =  self.google_response[0].raw['address_components'][state_index]['short_name']
        
        if country_index == None:
             self.standard_address_country_long = ''
             self.standard_address_country_short = ''
        else:
             self.standard_address_country_long =  self.google_response[0].raw['address_components'][country_index]['long_name']
             self.standard_address_country_short =  self.google_response[0].raw['address_components'][country_index]['short_name']
        
        if zip_code_index == None:
             self.standard_address_zip_code_long = ''
             self.standard_address_zip_code_short = ''
        else:
             self.standard_address_zip_code_long =  self.google_response[0].raw['address_components'][zip_code_index]['long_name']
             self.standard_address_zip_code_short =  self.google_response[0].raw['address_components'][zip_code_index]['short_name']
        
        if zip_code_suffix_index == None:
             self.standard_address_zip_code_suffix_long = ''
             self.standard_address_zip_code_suffix_short = ''
        else:
             self.standard_address_zip_code_suffix_long =  self.google_response[0].raw['address_components'][zip_code_suffix_index]['long_name']
             self.standard_address_zip_code_suffix_short =  self.google_response[0].raw['address_components'][zip_code_suffix_index]['short_name']

def google_response_by_coordinates (geo_data_path,
                                    output_path,
                                    id_field_name,
                                    long_field_name,
                                    lat_field_name,
                                    api_key,
                                    save_reponse_object = True):
    
    if isinstance(geo_data_path, pd.DataFrame):
        geo_data = geo_data_path
    else:
        geo_data = pd.read_csv(geo_data_path, header = 0, low_memory = False)
        
     #Making a new directory to save google responses as pickle files
    if  save_reponse_object:
        google_geocoder_data_path = output_path + 'Google_Response_Coordinates'
        try:  
            os.mkdir(google_geocoder_data_path)
        except OSError:  
            print ("Creation of the directory %s failed" % google_geocoder_data_path)
            sys.exit()
   
    geolocator = GoogleV3(api_key = api_key, timeout=None)
    
    gps_id = []
    latitude = []
    longitude = []
    one_line_address = []
    standard_address_street_number_long = []
    standard_address_street_number_short = []
    standard_address_route_long = []
    standard_address_route_short = []
    standard_address_city_long = []
    standard_address_city_short = []
    standard_address_county_long = []
    standard_address_county_short = []
    standard_address_state_long = []
    standard_address_state_short = []
    standard_address_country_long = []
    standard_address_country_short = []
    standard_address_zip_code_long = []
    standard_address_zip_code_short = []
    standard_address_zip_code_suffix_long = []
    standard_address_zip_code_suffix_short = []
    
    
    for row in range(len(geo_data)):
        print(row)
        
        #getting the lat and long from geo_data (input) and run it through class
                
        result = Google_geocoder_coordinate (gps_id = geo_data.at[row, id_field_name],
                                             long = geo_data.at[row, long_field_name],
                                             lat = geo_data.at[row, lat_field_name])      
        # creating the list of gps_id
        gps_id.append(geo_data.at[row, id_field_name])
    
        #adding info of location_info_from_google dataframe from google response
        latitude.append(result.lat)
        longitude.append(result.long)
        one_line_address.append(result.one_line_address)
        
        standard_address_street_number_long.append(result.standard_address_street_number_long)
        standard_address_street_number_short.append(result.standard_address_street_number_short)
        standard_address_route_long.append(result.standard_address_route_long)
        standard_address_route_short.append(result.standard_address_route_short)
        standard_address_city_long.append(result.standard_address_city_long)
        standard_address_city_short.append(result.standard_address_city_short)
        standard_address_county_long.append(result.standard_address_county_long)
        standard_address_county_short.append(result.standard_address_county_short)
        standard_address_state_long.append(result.standard_address_state_long)
        standard_address_state_short.append(result.standard_address_state_short)
        standard_address_country_long.append(result.standard_address_country_long)
        standard_address_country_short.append(result.standard_address_country_short)
        standard_address_zip_code_long.append(result.standard_address_zip_code_long)
        standard_address_zip_code_short.append(result.standard_address_zip_code_short)
        standard_address_zip_code_suffix_long.append(result.standard_address_zip_code_suffix_long)
        standard_address_zip_code_suffix_short.append(result.standard_address_zip_code_suffix_short)
        
        if  save_reponse_object:
            #saving google response as pickle file
            google_pickle_path = f'{google_geocoder_data_path}/google_geocoder_{geo_data.at[row, id_field_name]}.pkl' 
            save_object(result.google_response, google_pickle_path)
        
    # creating location_info_from_google dataframe
    location_info_from_google = pd.DataFrame(
            {'GPS_ID' : gps_id,
             'Latitude' : latitude,
             'Longitude' : longitude,
             'One_Line_Address' : one_line_address,
             'Street_Number_Long' : standard_address_street_number_long,
             'Street_Number_short' : standard_address_street_number_short,
             'Route_Long' : standard_address_route_long,
             'Route_Short' : standard_address_route_short,
             'City_Long' : standard_address_city_long,
             'City_Short' : standard_address_city_short,
             'County_Long' : standard_address_county_long,
             'Couny_Short' : standard_address_county_short,
             'State_Long' : standard_address_state_long,
             'State_Short' : standard_address_state_short,
             'Country_Long' : standard_address_country_long,
             'Country_Short' : standard_address_country_short,
             'Zip_Code_Long' : standard_address_zip_code_long,
             'Zip_Code_Short' : standard_address_zip_code_short,
             'Zip_Code_Suffix_Long' : standard_address_zip_code_suffix_long,
             'Zip_Code_Suffix_Short' : standard_address_zip_code_suffix_short
            })
    # saving location_info_from_google dataframe
    location_info_from_google.to_csv(f'{output_path}Location_Info_from_Google_by_Coordinates.csv', index = False, header = True)



def google_response_by_address (geo_data_path,
                                output_path,
                                api_key,
                                id_field_name,
                                street_field_name = None,
                                city_field_name = None,
                                state_field_name = None,
                                postal_code_field_name = None,
                                country_field_name = "US",
                                one_line_address_field_name = None,
                                save_reponse_object = True):
    
    if isinstance(geo_data_path, pd.DataFrame):
        geo_data = geo_data_path
    else:
        geo_data = pd.read_csv(geo_data_path, header = 0, low_memory = False)
        
     #Making a new directory to save google responses as pickle files
    if  save_reponse_object:
        google_geocoder_data_path = output_path + 'Google_Response_Address'
        try:  
            os.mkdir(google_geocoder_data_path)
        except OSError:  
            print ("Creation of the directory %s failed" % google_geocoder_data_path)
            sys.exit()
   
    geolocator = GoogleV3(api_key = api_key, timeout=None)
    
    gps_id = []
    latitude = []
    longitude = []
    one_line_address = []
    standard_address_street_number_long = []
    standard_address_street_number_short = []
    standard_address_route_long = []
    standard_address_route_short = []
    standard_address_city_long = []
    standard_address_city_short = []
    standard_address_county_long = []
    standard_address_county_short = []
    standard_address_state_long = []
    standard_address_state_short = []
    standard_address_country_long = []
    standard_address_country_short = []
    standard_address_zip_code_long = []
    standard_address_zip_code_short = []
    standard_address_zip_code_suffix_long = []
    standard_address_zip_code_suffix_short = []
    
    for row in range(len(geo_data)):
        print(row)
        
        #getting the lat and long from geo_data (input) and run it through class
        
                
        result = Google_geocoder_address (gps_id = geo_data.at[row, id_field_name],
                                          street = str(geo_data.at[row, street_field_name]),
                                          city = str(geo_data.at[row, city_field_name]),
                                          state = str(geo_data.at[row, state_field_name]),
                                          postal_code = str(geo_data.at[row, postal_code_field_name]))
        # creating the list of gps_id
        gps_id.append(geo_data.at[row, id_field_name])
    
        #adding info of location_info_from_google dataframe from google response
        latitude.append(result.lat)
        longitude.append(result.long)
        one_line_address.append(result.one_line_address)
        
        standard_address_street_number_long.append(result.standard_address_street_number_long)
        standard_address_street_number_short.append(result.standard_address_street_number_short)
        standard_address_route_long.append(result.standard_address_route_long)
        standard_address_route_short.append(result.standard_address_route_short)
        standard_address_city_long.append(result.standard_address_city_long)
        standard_address_city_short.append(result.standard_address_city_short)
        standard_address_county_long.append(result.standard_address_county_long)
        standard_address_county_short.append(result.standard_address_county_short)
        standard_address_state_long.append(result.standard_address_state_long)
        standard_address_state_short.append(result.standard_address_state_short)
        standard_address_country_long.append(result.standard_address_country_long)
        standard_address_country_short.append(result.standard_address_country_short)
        standard_address_zip_code_long.append(result.standard_address_zip_code_long)
        standard_address_zip_code_short.append(result.standard_address_zip_code_short)
        standard_address_zip_code_suffix_long.append(result.standard_address_zip_code_suffix_long)
        standard_address_zip_code_suffix_short.append(result.standard_address_zip_code_suffix_short)
        
        if  save_reponse_object:
            #saving google response as pickle file
            google_pickle_path = f'{google_geocoder_data_path}/google_geocoder_{geo_data.at[row, id_field_name]}.pkl' 
            save_object(result.google_response, google_pickle_path)
        
    # creating location_info_from_google dataframe
    location_info_from_google = pd.DataFrame(
            {'GPS_ID' : gps_id,
             'Latitude' : latitude,
             'Longitude' : longitude,
             'One_Line_Address' : one_line_address,
             'Street_Number_Long' : standard_address_street_number_long,
             'Street_Number_short' : standard_address_street_number_short,
             'Route_Long' : standard_address_route_long,
             'Route_Short' : standard_address_route_short,
             'City_Long' : standard_address_city_long,
             'City_Short' : standard_address_city_short,
             'County_Long' : standard_address_county_long,
             'Couny_Short' : standard_address_county_short,
             'State_Long' : standard_address_state_long,
             'State_Short' : standard_address_state_short,
             'Country_Long' : standard_address_country_long,
             'Country_Short' : standard_address_country_short,
             'Zip_Code_Long' : standard_address_zip_code_long,
             'Zip_Code_Short' : standard_address_zip_code_short,
             'Zip_Code_Suffix_Long' : standard_address_zip_code_suffix_long,
             'Zip_Code_Suffix_Short' : standard_address_zip_code_suffix_short
            })
    # saving location_info_from_google dataframe
    location_info_from_google.to_csv(f'{output_path}Location_Info_from_Google_by_Address.csv', index = False, header = True)
#setting the main path and output path
main_path = 'C:/Users/Yashar/Google Drive/UT HSC/Projects/Brownsville/New_project/'
output_path = 'C:/Users/Yashar/Google Drive/UT HSC/Projects/Brownsville/New_project/Output/'

#Setting the path to the geo location file
geo_data_path = main_path + 'geo_lookup.csv'
geo_data = pd.read_csv(geo_data_path, header = 0, low_memory = False)
for row in range(len(geo_data)):
    try:
        int(geo_data.at[row, 'Address_Line'].split(' ', 1)[0])
    except Exception:
        geo_data.at[row, 'Address_Line'] = geo_data.at[row, 'Address_Line2']
            

my_api_key = 

google_response_by_address (geo_data_path = geo_data,
                            output_path = output_path,
                            id_field_name = 'exid',
                            street_field_name = 'Address_Line',
                            city_field_name = 'City',
                            state_field_name = 'State',
                            postal_code_field_name = 'GI_ZIP',
                            save_reponse_object = True,
                            api_key = my_api_key)

google_response_by_coordinates (geo_data_path = geo_data,
                                output_path = output_path,
                                id_field_name = 'exid',
                                long_field_name = 'Address_Line',
                                lat_field_name = 'City',
                                save_reponse_object = True,
                                api_key = my_api_key)


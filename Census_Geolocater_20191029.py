# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 19:19:45 2019

@author: Yashar
"""
import pandas as pd
import numpy as np
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle
import os
import sys
import censusgeocode as cg
import time
    
# module to save census response as pickle file
def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, -1)
    
# module to load census response pickle file
def load_object(filename):
    with open(filename, 'rb') as input: # Overwrites any existing file.
        return pickle.load(input)

# Census_geocoder_address is class that sends request (address partitions) to census api
# and gets the response and parse it (tries is the number of retries to send request and
# get response each retry has 3 seconds delay. This is to prevent temporary internet problem)
class Census_geocoder_address:
    def __init__ (self, gps_id, street, city, state, zipcode, tries = 5):
        for _ in range(tries):
            try:
                self.census_response = cg.address(street,
                                                  city = city,
                                                  state = state,
                                                  zipcode = int(zipcode))
            
            except Exception as e:
                if _ < tries - 1: # _ is zero indexed
                    time.sleep(3)
                    continue
                else:
                    print(e)
                    pass
                    
        
        #adding info of location_info_from_census dataframe from google response
        try:
            self.long = self.census_response[0]['coordinates']['x']
            self.lat = self.census_response[0]['coordinates']['y']
            self.block_group = self.census_response[0]['geographies']['2010 Census Blocks'][0]['BLKGRP']
            self.block = self.census_response[0]['geographies']['2010 Census Blocks'][0]['BLOCK']
            self.county = self.census_response[0]['geographies']['2010 Census Blocks'][0]['COUNTY']
            self.geo_id = self.census_response[0]['geographies']['2010 Census Blocks'][0]['GEOID']
            self.object_id = self.census_response[0]['geographies']['2010 Census Blocks'][0]['OID']
            self.state = self.census_response[0]['geographies']['2010 Census Blocks'][0]['STATE']
            self.tract = self.census_response[0]['geographies']['2010 Census Blocks'][0]['TRACT']
            self.matched_address = self.census_response[0]['matchedAddress']
            self.tigerline_id = self.census_response[0]['tigerLine']['tigerLineId']
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
            self.matched_address = ''
            self.tigerline_id = np.nan
            print ('on gps_id: ', gps_id, "\n", e)

# Census_geocoder_address is class that sends request (coordinates) to census api
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
            self.block_group = self.census_response['2010 Census Blocks'][0]['BLKGRP']
            self.block = self.census_response['2010 Census Blocks'][0]['BLOCK']
            self.county = self.census_response['2010 Census Blocks'][0]['COUNTY']
            self.geo_id = self.census_response['2010 Census Blocks'][0]['GEOID']
            self.object_id = self.census_response['2010 Census Blocks'][0]['OID']
            self.state = self.census_response['2010 Census Blocks'][0]['STATE']
            self.tract = self.census_response['2010 Census Blocks'][0]['TRACT']
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

# census_response_by_address is the function that gets the data file (loads the geo_data_path if it is not dataframe)
# Then uses the Census_geocoder_address class to create geolocation file and save it in output path
def census_response_by_address (geo_data_path,
                               output_path,
                               id_field_name,
                               street_field_name,
                               city_field_name,
                               state_field_name,
                               zipcode_field_name,
                               save_reponse_object = True):
    if isinstance(geo_data_path, pd.DataFrame):
        geo_data = geo_data_path
    else:
        geo_data = pd.read_csv(geo_data_path, header = 0, low_memory = False)
    census_geocoder_data_path = output_path + 'Census_Response_Address'
    try:  
        os.mkdir(census_geocoder_data_path)
    except OSError:  
        print ("Creation of the directory %s failed" % census_geocoder_data_path)
        sys.exit()
    gps_id = []
    census_long = []
    census_lat = []
    census_block_group = []
    census_block = []
    census_county = []
    census_geo_id = []
    census_object_id = []
    census_state = []
    census_tract = []
    census_matched_address = []
    census_tigerline_id = []
    for row in range(len(geo_data)):
        print(row)
       # creating the list of gps_id
        gps_id.append(geo_data.at[row, id_field_name])
        result = Census_geocoder_address (gps_id = geo_data.at[row, id_field_name],
                                          street = geo_data.at[row, street_field_name],
                                          city = geo_data.at[row, city_field_name],
                                          state = geo_data.at[row, state_field_name],
                                          zipcode = geo_data.at[row, zipcode_field_name])
        census_long.append(result.long)
        census_lat.append(result.lat)
        census_block_group.append(result.block_group)
        census_block.append(result.block)
        census_county.append(result.county)
        census_geo_id.append(result.geo_id)
        census_object_id.append(result.object_id)
        census_state.append(result.state)
        census_tract.append(result.tract)
        census_matched_address.append(result.matched_address)
        census_tigerline_id.append(result.tigerline_id)
        
        
        #saving census response as pickle file if  save_reponse_object = True
        if  save_reponse_object:
            census_pickle_path = f'{census_geocoder_data_path}/census_geocoder_{geo_data.at[row,id_field_name]}.pkl' 
            save_object(result.census_response, census_pickle_path)
        
    


    # creating location_info_from_census dataframe
    location_info_from_census = pd.DataFrame(
            {'GPS_ID' : gps_id,
             'Census_long' : census_long,
             'Census_lat' : census_lat,
             'Census_Block_Group' : census_block_group,
             'Census_Block' : census_block,
             'Census_County' : census_county,
             'Census_Geo_ID' : census_geo_id,
             'Census_Object_ID' : census_object_id,
             'Census_State' : census_state,
             'Census_Tract' : census_tract,
             'Census_Matched_Address' : census_matched_address,
             'Census_Tigerline_ID' : census_tigerline_id
            })
    # saving location_info_from_census dataframe
    location_info_from_census.to_csv(f'{output_path}Location_Info_from_Census_by_Address.csv', index = False, header = True)

# census_response_by_address is the function that gets the data file (loads the geo_data_path if it is not dataframe)
# Then uses the Census_geocoder_address class to create geolocation file and save it in output path
def census_response_by_coordinates (geo_data_path,
                                    output_path,
                                    id_field_name,
                                    long_field_name,
                                    lat_field_name,
                                    save_reponse_object = True):
    if isinstance(geo_data_path, pd.DataFrame):
        geo_data = geo_data_path
    else:
        geo_data = pd.read_csv(geo_data_path, header = 0, low_memory = False)
    census_geocoder_data_path = output_path + 'Census_Response_Coordinates'
    try:  
        os.mkdir(census_geocoder_data_path)
    except OSError:  
        print ("Creation of the directory %s failed" % census_geocoder_data_path)
        sys.exit()
    gps_id = []
    census_long = []
    census_lat = []
    census_block_group = []
    census_block = []
    census_county = []
    census_geo_id = []
    census_object_id = []
    census_state = []
    census_tract = []
    for row in range(len(geo_data)):
        print(row)
       # creating the list of gps_id
        gps_id.append(geo_data.at[row, id_field_name])
        result = Census_geocoder_coordinate (gps_id = geo_data.at[row, id_field_name],
                                             long = geo_data.at[row, long_field_name],
                                             lat = geo_data.at[row, lat_field_name])
        census_long.append(result.long)
        census_lat.append(result.lat)
        census_block_group.append(result.block_group)
        census_block.append(result.block)
        census_county.append(result.county)
        census_geo_id.append(result.geo_id)
        census_object_id.append(result.object_id)
        census_state.append(result.state)
        census_tract.append(result.tract)
        
        #saving census response as pickle file if  save_reponse_object = True
        if  save_reponse_object:
            census_pickle_path = f'{census_geocoder_data_path}/census_geocoder_{geo_data.at[row,id_field_name]}.pkl' 
            try:
                save_object(result.census_response, census_pickle_path)
            except:
                pass
        
    


    # creating location_info_from_census dataframe
    location_info_from_census = pd.DataFrame(
            {'GPS_ID' : gps_id,
             'Census_long' : census_long,
             'Census_lat' : census_lat,
             'Census_Block_Group' : census_block_group,
             'Census_Block' : census_block,
             'Census_County' : census_county,
             'Census_Geo_ID' : census_geo_id,
             'Census_Object_ID' : census_object_id,
             'Census_State' : census_state,
             'Census_Tract' : census_tract,
            })
    # saving location_info_from_census dataframe
    location_info_from_census.to_csv(f'{output_path}Location_Info_from_Census_by_Coordinates.csv', index = False, header = True)
    
    
#setting the main path and output path
main_path = 'D:/Google Drive/UT HSC/Projects/Brownsville/New_project/'
output_path = 'D:/Google Drive/UT HSC/Projects/Brownsville/New_project/Output/'

#Setting the path to the geo location file
geo_data_path = main_path + 'geo_lookup.csv'
geo_data = pd.read_csv(geo_data_path, header = 0, low_memory = False)
for row in range(len(geo_data)):
    try:
        int(geo_data.at[row, 'Address_Line'].split(' ', 1)[0])
    except Exception:
        geo_data.at[row, 'Address_Line'] = geo_data.at[row, 'Address_Line2']
            

census_response_by_address (geo_data_path = geo_data,
                            output_path = output_path,
                            id_field_name = 'exid',
                            street_field_name = 'Address_Line',
                            city_field_name = 'City',
                            state_field_name = 'State',
                            zipcode_field_name = 'GI_ZIP',
                            save_reponse_object = True)
main_path = 'C:/Users/Yashar/Google Drive/UT HSC/Projects/Brownsville/New_project/'
output_path = 'C:/Users/Yashar/Google Drive/UT HSC/Projects/Brownsville/New_project/Output/'
path_for_census_coordinate = main_path + "Output/Location_Info_from_Google_by_Address.csv"
census_response_by_coordinates (geo_data_path = path_for_census_coordinate,
                                output_path = output_path,
                                id_field_name = 'GPS_ID',
                                long_field_name = 'Longitude',
                                lat_field_name = 'Latitude',
                                save_reponse_object = True)


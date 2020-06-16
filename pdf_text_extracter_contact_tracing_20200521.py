# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 12:28:19 2020

@author: Yashar
"""
# =========================================================================== #
# you need to install Tessaract OCR on your machine. Use following link:      #
#     https://tesseract-ocr.github.io/tessdoc/Home.html                       #
# the following packages are needed:                                          #
# geopy: conda install -c conda-forge geopy                                   #
# censusgeocode: conda install -c mikesilva censusgeocode                     #
# PyMuPDF (fitz): pip install PyMuPDF                                         #
# =========================================================================== #
    
    
################################ Importing Modules ############################
# =============================================================================
# from pdf2image import convert_from_path, convert_from_bytes
# from pdf2image.exceptions import (
# PDFInfoNotInstalledError,
# PDFPageCountError,
# PDFSyntaxError
# )
# =============================================================================
import fitz
from PIL import Image
import pytesseract
import cv2
import os
import pandas as pd
import glob
import numpy as np
from geopy.geocoders import GoogleV3
import censusgeocode as cg
import time
import datetime
import io

################################ Setting the path #############################
### define the folder that contains pdf files
pdf_folder = 'C:/Users/Yashar/Google Drive/UT HSC/Projects/COVID_19/PDFtoText/Contact_Tracing/'
### define the folder to save the results
output_folder = 'C:/Users/Yashar/Google Drive/UT HSC/Projects/COVID_19/PDFtoText/Contact_Tracing/'
### define the path to tessaract.exe that will be used by pytessaract (OCR)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

### setiing up google geolocater ###
api_key = 'AIzaSyBl9S9gI9qe8uFzWeJwDKjY2XU0_mqZuLw' #####Put your API key here
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


#### pdf2image method ####
# =============================================================================
# pages = convert_from_path(f'{pdf_folder}04.10.2020_CM_CC213I.pdf',
#                           dpi=500,
#                           grayscale=True)
# i = 1
# for page in pages:
#     page.save(f'{output_folder}{i}.jpg', 'JPEG')
#     i+=1
# pages = convert_from_bytes(open(r'/Users/Robotnic/Desktop/companyprofile.pdf','rb').read())
# =============================================================================

#### fitz method ####
# =============================================================================
# doc = fitz.open(f'{pdf_folder}04.10.2020_CM_CC213I.pdf')
# page = doc.loadPage(0) #number of page
# mat = fitz.Matrix(500/72, 500/72)
# pix = page.getPixmap(matrix = mat)
# pix.writePNG(f'{output_folder}t.png')
# =============================================================================



# =============================================================================
# The pdf file structure. it is a dictionaty with each page as a key. each page 
# by itself is a dictionary with item number as a key. we have 3 different entries:
#     1- text box: first entry is field name, second is a tuple of upper corner x,y
#     and lower corner x,y to crop the image to pass to OCR, third is the type of
#     the field to envoke the appropriate function, fourth is indicator that if the
#     text box has the title inside or not.
#     2- check box: first entry is field name, second is a tuple of upper corner x,y
#     and lower corner x,y to crop the image to do image processing, third is the type of
#     the field to envoke the appropriate function, fourth is the list of values if
#     the box is checked or not.
#     3- radio button: first entry is field name, second is a list of tuples of 
#     upper corner x,y and lower corner x,y to crop the image to do image processing,
#     third is the type of the field to envoke the appropriate function,
#     fourth is the list of values if for the selected radio button.
# =============================================================================
pdf_structure = {"Page_1":{ 1:["state_local_close_id", (2735,380,3897,527), "text box", ["without title"]],
                            2:["case_last_name", (936,1605,2421,1689), "text box", ["without title"]],
                            3:["case_first_name", (2627,1605,3997,1689), "text box", ["without title"]],
                            4:["symptomatic", [(2510,1796,2582,1868),(2510,1931,2582,2003)], "radio button", [0, 1]],
                            5:["date_of_symptom_onset", (), "space retainer", ["without title"]],
                            6:["date_of_symptom_onset_month", (1034,1776,1169,1866), "digit box", ["without title"]],
                            7:["date_of_symptom_onset_day", (1202,1776,1373,1866), "digit box", ["without title"]],
                            8:["date_of_symptom_onset_year", (1404,1776,1681,1866), "digit box", ["without title"]],
                            9:["date_of_last_symptom", (), "space retainer", ["without title"]],
                            10:["date_of_last_symptom_month", (2160,668,2922,796), "digit box", ["without title"]],
                            11:["date_of_last_symptom_day", (2927,668,3510,796), "digit box", ["without title"]],
                            12:["date_of_last_symptom_year", (3514,668,3997,796), "digit box", ["without title"]],
                            13:["date_of_last_exposure", (), "space retainer", ["without title"]],
                            14:["date_of_last_exposure_month", (1957,2105,2093,2203), "digit box", ["without title"]],
                            15:["date_of_last_exposure_day", (2125,2105,2296,2203), "digit box", ["without title"]],
                            16:["date_of_last_exposure_year", (2327,2105,2604,2203), "digit box", ["without title"]],
                            17:["continued_exposure", (573,2228,644,2299), "check box", [1,0]],
                            18:["date_interview_completed", (), "space retainer", ["without title"]],
                            19:["date_interview_completed_month", (1171,2455,1309,2539), "digit box", ["without title"]],
                            20:["date_interview_completed_day", (1340,2455,1511,2539), "digit box", ["without title"]],
                            21:["date_interview_completed_year", (1541,2455,1819,2539), "digit box", ["without title"]],
                            22:["interview_telephone", (3132,2455,3932,2539), "digit box", ["without title"]],
                            23:["interviewer_lastname", (1069,2600,1640,2678), "text box", ["without title"]],
                            24:["interviewer_firstname", (1847,2600,2533,2678), "text box", ["without title"]],
                            25:["interviewer_org", (3311,2600,3919,2678), "text box", ["without title"]],
                            26:["info_provider", [(760,2888,832,2959),(1285,2888,1356,2959),(760,3028,832,3099)], "radio button", [0,1,2]],
                            27:["other_name_specify", (1507,3020,2154,3097), "text box", ["without title"]],
                            28:["relationship_to_contact", (2944,3020,3896,3097), "text box", ["without title"]],
                            29:["contact_primary_language", (1214,3150,1973,3238), "text box", ["without title"]],
                            30:["translator", [(3430,3197,3459,3226),(3651,3197,3680,3226)], "radio button", [1,0]],
                            31:["contact_last_name", (310,3425,1837,3605), "text box", ["with title", "Last Name:"]],
                            32:["contact_first_name", (2180,3425,3931,3605), "text box", ["with title", "First Name:"]],
                            33:["contact_current_address", (310,3635,1379,3820), "text box", ["with title", "Current Address:"]],
                            34:["contact_city", (1508,3635,2080,3820), "text box", ["with title", "City:"]],
                            35:["contact_state", (2179,3635,3017,3820), "text box", ["with title", "State:"]],
                            36:["contact_zip_code", (3122,3635,3960,3820), "text box", ["with title", "Zip:"]],
                            37:["contact_fips_code", (), "space retainer", ["without title"]],
                            38:["contact_lat", (), "space retainer", ["without title"]],
                            39:["contact_long", (), "space retainer", ["without title"]],
                            40:["contact_phone", (551,3930,1426,4034), "digit box", ["without title"]],
                            41:["same_address_as_case", [(3229,3993,3258,4022),(3450,3993,3479,4022)], "radio button", [1,0]],
                            42:["contact_date_of_birth", (), "space retainer", ["without title"]],
                            43:["contact_date_of_birth_month", (850,4300,1064,4406), "digit box", ["without title"]],
                            44:["contact_date_of_birth_day", (1094,4300,1316,4406), "digit box", ["without title"]],
                            45:["contact_date_of_birth_year", (1344,4300,1565,4406), "digit box", ["without title"]],
                            46:["contact_age", (2623,4300,2750,4406), "digit box", ["without title"]],
                            47:["contact_age_unit", [(2991,4337,3062,4408),(3302,4337,3373,4408),(3653,4337,3725,4408)], "radio button", [0,1,2]],
                            48:["contact_ethnicity", [(754,4492,826,4564),(1576,4492,1648,4564),(2326,4492,2398,4564)], "radio button", [0,1,2]],
                            49:["contact_race", [(649,4633,721,4704),(1001,4633,1072,4704),(1297,4633,1369,4704),(2380,4633,2452,4704),(2689,4633,2760,4704),(446,4773,518,4844),(1892,4773,1964,4844)], "radio button", [0,1,2,3,4,6,5]],
                            50:["cotact_other_race", (999,4740,1760,4843), "text box", ["without title"]],
                            51:["contact_sex", [(607,4975,678,5047),(1048,4975,1119,5047),(1826,4975,1898,5047),(2326,4975,2398,5047)], "radio button", [0,1,2,3]]
                           },
                 "Page_2":{ 1:["exp_symptoms", (1034,808,1106,879), "check box", [1,0]],
                            2:["symptom_fever_gt_100f", [(1510,1131,1581,1202),(1759,1131,1830,1202),(2025,1131,2097,1202)], "radio button", [1,0,2]],
                            3:["symptom_fevergt100_notresolved", (3744,1131,3816,1202), "check box", [1,0]],
                            4:["symptom_fevergt100_onset", (2189,1114,2887,1220), "text box", ["without title"]],
                            5:["symptom_fevergt100_resolved", (2892,1114,3590,1220), "text box", ["without title"]],
                            6:["symptom_fever_sub", [(1510,1242,1581,1313),(1759,1242,1830,1313),(2025,1242,2097,1313)], "radio button", [1,0,2]],
                            7:["symptom_feversub_notresolved", (3744,1242,3816,1313), "check box", [1,0]],
                            8:["symptom_feversub_onset", (2189,1224,2887,1330), "text box", ["without title"]],
                            9:["symptom_feversub_resolved", (2892,1224,3590,1330), "text box", ["without title"]],
                            10:["symptom_chills", [(1510,1352,1581,1423),(1759,1352,1830,1423),(2025,1352,2097,1423)], "radio button", [1,0,2]],
                            11:["symptom_chills_notresolved", (3744,1352,3816,1423), "check box", [1,0]],
                            12:["symptom_chills_onset", (2189,1335,2887,1442), "text box", ["without title"]],
                            13:["symptom_chills_resolved", (2892,1335,3590,1442), "text box", ["without title"]],
                            14:["symptom_myalgia", [(1510,1463,1581,1534),(1759,1463,1830,1534),(2025,1463,2097,1534)], "radio button", [1,0,2]],
                            15:["symptom_myalgia_notresolved", (3744,1463,3816,1534), "check box", [1,0]],
                            16:["symptom_myalgia_onset", (2189,1446,2887,1553), "text box", ["without title"]],
                            17:["symptom_myalgia_resolved", (2892,1446,3590,1553), "text box", ["without title"]],
                            18:["symptom_rhinorrhea", [(1510,1574,1581,1645),(1759,1574,1830,1645),(2025,1574,2097,1645)], "radio button", [1,0,2]],
                            19:["symptom_rhinorrhea_notresolved", (3744,1574,3816,1645), "check box", [1,0]],
                            20:["symptom_rhinorrhea_onset", (2189,1557,2887,1663), "text box", ["without title"]],
                            21:["symptom_rhinorrhea_resolved", (2892,1557,3590,1663), "text box", ["without title"]],
                            22:["symptom_sorethroat", [(1510,1685,1581,1756),(1759,1685,1830,1756),(2025,1685,2097,1756)], "radio button", [1,0,2]],
                            23:["symptom_sorethroat_notresolved", (3744,1685,3816,1756), "check box", [1,0]],
                            24:["symptom_sorethroat_onset", (2189,1667,2887,1774), "text box", ["without title"]],
                            25:["symptom_sorethroat_resolved", (2892,1667,3590,1774), "text box", ["without title"]],
                            26:["symptom_cough", [(1510,1841,1581,2070),(1759,1841,1830,2070),(2025,1841,2097,2070)], "radio button", [1,0,2]],
                            27:["symptom_cough_notresolved", (3744,1841,3816,2070), "check box", [1,0]],
                            28:["symptom_cough_onset", (2189,1778,2887,1978), "text box", ["without title"]],
                            29:["symptom_cough_resolved", (2892,1778,3590,1978), "text box", ["without title"]],
                            30:["symptom_dyspnea", [(1510,1999,1581,2070),(1759,1999,1830,2070),(2025,1999,2097,2070)], "radio button", [1,0,2]],
                            31:["symptom_dyspnea_notresolved", (3744,1999,3816,2070), "check box", [1,0]],
                            32:["symptom_dyspnea_onset", (2189,1982,2887,2088), "text box", ["without title"]],
                            33:["symptom_dyspnea_resolved", (2892,1982,3590,2088), "text box", ["without title"]],
                            34:["symptom_nausea", [(1510,2110,1581,2181),(1759,2110,1830,2181),(2025,2110,2097,2181)], "radio button", [1,0,2]],
                            35:["symptom_nausea_notresolved", (3744,2110,3816,2181), "check box", [1,0]],
                            36:["symptom_nausea_onset", (2189,2092,2887,2199), "text box", ["without title"]],
                            37:["symptom_nausea_resolved", (2892,2092,3590,2199), "text box", ["without title"]],
                            38:["symptom_headache", [(1510,2220,1581,2291),(1759,2220,1830,2291),(2025,2220,2097,2291)], "radio button", [1,0,2]],
                            39:["symptom_headache_notresolved", (3744,2220,3816,2291), "check box", [1,0]],
                            40:["symptom_headache_onset", (2189,2203,2887,2309), "text box", ["without title"]],
                            41:["symptom_headache_resolved", (2892,2203,3590,2309), "text box", ["without title"]],
                            42:["symptom_abpain", [(1510,2330,1581,2402),(1759,2330,1830,2402),(2025,2330,2097,2402)], "radio button", [1,0,2]],
                            43:["symptom_abpain_notresolved", (3744,2330,3816,2402), "check box", [1,0]],
                            44:["symptom_abpain_onset", (2189,2314,2887,2420), "text box", ["without title"]],
                            45:["symptom_abpain_resolved", (2892,2314,3590,2420), "text box", ["without title"]],
                            46:["symptom_diarrhea", [(1510,2488,1581,2559),(1759,2488,1830,2559),(2025,2488,2097,2559)], "radio button", [1,0,2]],
                            47:["symptom_diarrhea_notresolved", (3744,2488,3816,2559), "check box", [1,0]],
                            48:["symptom_diarrhea_onset", (2189,2425,2887,2624), "text box", ["without title"]],
                            49:["symptom_diarrhea_resolved", (2892,2425,3590,2624), "text box", ["without title"]],
                            50:["symptom_other", [(1510,2705,1581,2776),(1759,2705,1830,2776),(2025,2705,2097,2776)], "radio button", [1,0,2]],
                            51:["symptom_other_specify", (283,2628,1434,2854), "text box", ["with title", "Other, specify:"]],
                            52:["symptom_other_notresolved", (3744,2705,3816,2776), "check box", [1,0]],
                            53:["symptom_other_onset", (2189,2628,2887,2854), "text box", ["without title"]],
                            54:["symptom_other_resolved", (2892,2628,3590,2854), "text box", ["without title"]],
                            55:["preex_conditions", [(2200,3081,2280,3161),(2455,3081,2534,3161),(2691,3081,2771,3161)], "radio button", [1,0,2]],
                            56:["preex_copd", [(1590,3199,1662,3270),(1832,3199,1904,3270),(2073,3199,2144,3270)], "radio button", [1,0,2]],
                            57:["preex_copd_specify", (2346,3176,3998,3374), "text box", ["without title"]],
                            58:["preex_diabetes", [(1589,3401,1660,3473),(1825,3401,1897,3473),(2071,3401,2143,3473)], "radio button", [1,0,2]],
                            59:["preex_diabetes_specify", (2346,3379,3998,3484), "text box", ["without title"]],
                            60:["preex_cardio", [(1589,3511,1660,3582),(1825,3511,1897,3582),(2071,3511,2143,3582)], "radio button", [1,0,2]],
                            61:["preex_cardio_specify", (2346,3488,3998,3593), "text box", ["without title"]],
                            62:["preex_renal", [(1589,3620,1660,3691),(1825,3620,1897,3691),(2071,3620,2143,3691)], "radio button", [1,0,2]],
                            63:["preex_renal_specify", (2346,3597,3998,3702), "text box", ["without title"]],
                            64:["preex_liver", [(1589,3729,1660,3801),(1825,3729,1897,3801),(2071,3729,2143,3801)], "radio button", [1,0,2]],
                            65:["preex_liver_specify", (2346,3707,3998,3811), "text box", ["without title"]],
                            66:["preex_immuno", [(1589,3839,1660,3911),(1825,3839,1897,3911),(2071,3839,2143,3911)], "radio button", [1,0,2]],
                            67:["preex_immuno_specify", (2346,3816,3998,3921), "text box", ["without title"]],
                            68:["preex_neuro", [(1589,3948,1660,4020),(1825,3948,1897,4020),(2071,3948,2143,4020)], "radio button", [1,0,2]],
                            69:["preex_neuro_specify", (2346,3926,3998,4031), "text box", ["with title", "Specify:"]],
                            70:["preex_other_chronic", [(1589,4057,1660,4129),(1825,4057,1897,4129),(2071,4057,2143,4129)], "radio button", [1,0,2]],
                            71:["preex_other_specify", (2346,4035,3998,4140), "text box", ["with title", "Specify:"]],
                            72:["preex_pregnant", [(1589,4167,1660,4238),(1825,4167,1897,4238),(2071,4167,2143,4238)], "radio button", [1,0,2]],
                            73:["preex_pregnant_specify", (2346,4144,3998,4342), "text box", ["without title"]],
                            74:["preex_current_smoke", [(1589,4369,1660,4441),(1825,4369,1897,4441),(2071,4369,2143,4441)], "radio button", [1,0,2]],
                            75:["preex_current_smoke_specify", (2346,4347,3998,4451), "text box", ["with title", "Specify:"]],
                            76:["preex_former_smoke", [(1589,4478,1660,4550),(1825,4478,1897,4550),(2071,4478,2143,4550)], "radio button", [1,0,2]],
                            77:["preex_former_smoke_specify", (2346,4456,3998,4561), "text box", ["with title", "Specify:"]]
                          },
                 "Page_3":{ 1:["exposures_relationship_spouse", (298,801,378,881), "check box", [1,0]],
                            2:["exposures_relationship_child", (298,903,378,982), "check box", [1,0]],
                            3:["exposures_relationship_parent", (298,1004,378,1084), "check box", [1,0]],
                            4:["exposures_relationship_other_family", (298,1106,378,1186), "check box", [1,0]],
                            5:["exposures_relationship_friend", (298,1208,378,1288), "check box", [1,0]],
                            6:["exposures_relationship_healthcare", (1234,801,1314,881), "check box", [1,0]],
                            7:["exposures_relationship_co_worker", (1234,903,1314,982), "check box", [1,0]],
                            8:["exposures_relationship_classmate", (1234,1004,1314,1084), "check box", [1,0]],
                            9:["exposures_relationship_roommate", (1234,1106,1314,1186), "check box", [1,0]],
                            10:["exposures_relationship_other", (1234,1208,1314,1288), "check box", [1,0]],
                            11:["exposures_relationship_other_specify", (1868,1170,3405,1285), "text box", ["without title"]],
                            12:["exposures_exposed_household", (298,1621,378,1701), "check box", [1,0]],
                            13:["exposures_exposed_daycare", (298,1771,378,1851), "check box", [1,0]],
                            14:["exposures_exposed_rideshare", (298,1921,378,2001), "check box", [1,0]],
                            15:["exposures_exposed_other", (298,2071,378,2151), "check box", [1,0]],
                            16:["exposures_exposed_healthcare", (1183,1621,1263,1701), "check box", [1,0]],
                            17:["exposures_exposed_school", (1183,1771,1263,1851), "check box", [1,0]],
                            18:["exposures_exposed_hotel", (1183,1921,1263,2001), "check box", [1,0]],
                            19:["exposures_exposed_work", (2444,1621,2524,1701), "check box", [1,0]],
                            20:["exposures_exposed_transit", (2444,1771,2524,1851), "check box", [1,0]],
                            21:["exposures_exposed_community", (2444,1921,2524,2001), "check box", [1,0]],
                            22:["exposures_exposed_specify", (282,2200,4134,2732), "text box", ["with title", "Specify Location(s) (Name and Address):"]],
                            23:["exposure_face", [(1165,3517,1228,3581),(1165,3644,1228,3707),(1165,3771,1228,3834)], "radio button", [1,0,2]],
                            24:["exposure_face_start", (1627,3465,2185,3872), "text box", ["without title"]],
                            25:["exposure_face_end", (2190,3465,2780,3872), "text box", ["without title"]],
                            26:["exposure_face_occur", (2784,3465,3467,3872), "digit box", ["without title"]],
                            27:["exposure_face_total", (3472,3465,4123,3624), "digit box", ["without title"]],
                            28:["exposure_face_total_unit", [(3480,3646,3543,3709),(3826,3646,3889,3709),(3480,3772,3543,3836)], "radio button", [0,1,2]],
                            29:["exposure_physical", [(1165,3932,1228,3995),(1165,4058,1228,4121),(1165,4184,1228,4247)], "radio button", [1,0,2]],
                            30:["exposure_physical_start", (1627,3880,2185,4388), "text box", ["without title"]],
                            31:["exposure_physical_end", (2190,3880,2780,4388), "text box", ["without title"]],
                            32:["exposure_physical_occur", (2784,3880,3467,4388), "digit box", ["without title"]],
                            33:["exposure_physical_total", (3472,3880,4123,4038), "digit box", ["without title"]],
                            34:["exposure_physical_total_unit", [(3480,4059,3543,4122),(3826,4059,3889,4122),(3480,4186,3543,4249)], "radio button", [0,1,2]],
                            35:["exposure_6feet", [(1165,4446,1228,4511),(1165,4573,1228,4637),(1165,4700,1228,4763)], "radio button", [1,0,2]],
                            36:["exposure_6feet_start", (1627,4396,2185,4802), "text box", ["without title"]],
                            37:["exposure_6feet_end", (2190,4396,2780,4802), "text box", ["without title"]],
                            38:["exposure_6feet_occur", (2784,4396,3467,4802), "digit box", ["without title"]],
                            39:["exposure_6feet_total", (3472,4396,4123,4553), "digit box", ["without title"]],
                            40:["exposure_6feet_total_unit", [(3480,4575,3543,4638),(3826,4575,3889,4638),(3480,4702,3543,4765)], "radio button", [0,1,2]]
                          },
                 "Page_4":{ 1:["exposure_6feetwhile", [(1165,1158,1228,1221),(1165,1284,1228,1346),(1165,1410,1228,1473)], "radio button", [1,0,2]],
                            2:["exposure_6feetwhile_start", (1627,1106,2185,1512), "text box", ["without title"]],
                            3:["exposure_6feetwhile_end", (2190,1106,2780,1512), "text box", ["without title"]],
                            4:["exposure_6feetwhile_occur", (2784,1106,3467,1512), "digit box", ["without title"]],
                            5:["exposure_6feetwhile_total", (3472,1106,4123,1264), "digit box", ["without title"]],
                            6:["exposure_6feetwhile_total_unit", [(3480,1285,3543,1348),(3826,1285,3889,1348),(3480,1412,3543,1475)], "radio button", [0,1,2]],
                            7:["exposure_handled", [(1165,1572,1228,1635),(1165,1698,1228,1761),(1165,1825,1228,1888)], "radio button", [1,0,2]],
                            8:["exposure_handled_start", (1627,1520,2185,2129), "text box", ["without title"]],
                            9:["exposure_handled_end", (2190,1520,2780,2129), "text box", ["without title"]],
                            10:["exposure_handled_occur", (2784,1520,3467,2129), "digit box", ["without title"]],
                            11:["exposure_handled_total", (3472,1520,4123,1678), "digit box", ["without title"]],
                            12:["exposure_handled_total_unit", [(3480,1700,3543,1763),(3826,1700,3889,1763),(3480,1826,3543,1889)], "radio button", [0,1,2]],
                            13:["exposure_sameroom", [(1165,2189,1228,2252),(1165,2315,1228,2379),(1165,2442,1228,2505)], "radio button", [1,0,2]],
                            14:["exposure_sameroom_start", (1627,2137,2185,2517), "text box", ["without title"]],
                            15:["exposure_sameroom_end", (2190,2137,2780,2517), "text box", ["without title"]],
                            16:["exposure_sameroom_occur", (2784,2137,3467,2517), "digit box", ["without title"]],
                            17:["exposure_sameroom_total", (3472,2137,4123,2295), "digit box", ["without title"]],
                            18:["exposure_sameroom_total_unit", [(3480,2317,3543,2380),(3826,2317,3889,2380),(3480,2443,3543,2506)], "radio button", [0,1,2]],
                            19:["exposure_sameroomsleep", [(1165,2577,1228,2640),(1165,2703,1228,2766),(1165,2830,1228,2893)], "radio button", [1,0,2]],
                            20:["exposure_sameroomsleep_start", (1627,2525,2185,2931), "text box", ["without title"]],
                            21:["exposure_sameroomsleep_end", (2190,2525,2780,2931), "text box", ["without title"]],
                            22:["exposure_sameroomsleep_occur", (2784,2525,3467,2931), "digit box", ["without title"]],
                            23:["exposure_sameroomsleep_total", (3472,2525,4123,2683), "digit box", ["without title"]],
                            24:["exposure_sameroomsleep_total_unit", [(3480,2705,3543,2768),(3826,2705,3889,2768),(3480,2831,3543,2894)], "radio button", [0,1,2]],
                            25:["exposure_bathroom", [(1165,2990,1228,3054),(1165,3117,1228,3180),(1165,3244,1228,3307)], "radio button", [1,0,2]],
                            26:["exposure_bathroom_start", (1627,2939,2185,3345), "text box", ["without title"]],
                            27:["exposure_bathroom_end", (2190,2939,2780,3345), "text box", ["without title"]],
                            28:["exposure_bathroom_occur", (2784,2939,3467,3345), "digit box", ["without title"]],
                            29:["exposure_bathroom_total", (3472,2939,4123,3012), "digit box", ["without title"]],
                            30:["exposure_bathroom_total_unit", [(3480,3034,3543,3097),(3826,3034,3889,3097),(3480,3119,3543,3182)], "radio button", [0,1,2]],
                            31:["exposure_food", [(1165,3405,1228,3468),(1165,3531,1228,3594),(1165,3657,1228,3721)], "radio button", [1,0,2]],
                            32:["exposure_food_start", (1627,3353,2185,3709), "text box", ["without title"]],
                            33:["exposure_food_end", (2190,3353,2780,3709), "text box", ["without title"]],
                            34:["exposure_food_occur", (2784,3353,3467,3709), "digit box", ["without title"]],
                            35:["exposure_food_total", (3472,3353,4123,3426), "digit box", ["without title"]],
                            36:["exposure_food_total_unit", [(3480,3447,3543,3510),(3826,3447,3889,3510),(3480,3532,3543,3596)], "radio button", [0,1,2]],
                            37:["exposure_travel", [(1165,3815,1228,3878),(1165,3942,1228,4005),(1165,4068,1228,4131)], "radio button", [1,0,2]],
                            38:["exposure_travel_start", (1627,3763,2185,4271), "text box", ["without title"]],
                            39:["exposure_travel_end", (2190,3763,2780,4271), "text box", ["without title"]],
                            40:["exposure_travel_occur", (2784,3763,3467,4271), "digit box", ["without title"]],
                            41:["exposure_travel_total", (3472,3763,4123,3921), "digit box", ["without title"]],
                            42:["exposure_travel_total_unit", [(3480,3943,3543,4006),(3826,3943,3889,4006),(3480,4069,3543,4132)], "radio button", [0,1,2]]
                          }
                }


###Creating dataframe to store the results
column_names = ['File Name']
for page_structure in pdf_structure.values():
    for value in page_structure.values():
        column_names.append(value[0])
        
df = pd.DataFrame(columns = column_names)

### preprocess_image function. input is image and preprocess method
## thresh is standard method for OCR. converts image to black and white
## blur is noise reduction method for noisy document (will be used later)
## "detect rectangle" converts the image to grayscale for finding rectangle (will be used later)
def preprocess_image(image, preprocess = 'thresh'):   
    image = np.float32(image).astype(np.uint8)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if preprocess == "thresh":
    	gray = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # make a check to see if median blurring should be done to remove noise
    elif preprocess == "blur":
    	gray = cv2.medianBlur(gray, 3)
    elif preprocess == "detect rectangle":
        pass      
    return gray

### text_box_process function. input is page and value from pdf_structure dictionary
## if the text box is with title, It will remove the title from the text
def text_box_process (page, field_value):
    cropped=page.crop(field_value[1])
    preprocessed_image = preprocess_image(cropped)
    text = pytesseract.image_to_string(preprocessed_image)
    #remove newline character and leading white space
    result = text.replace('\n','').lstrip()
    if field_value[3][0] == "with title":
        result = result[len(field_value[3][1]):]
    result = result.lstrip()
    return result

def digit_box_process (page, field_value):
    cropped=page.crop(field_value[1])
    preprocessed_image = preprocess_image(cropped)
    text = pytesseract.image_to_string(preprocessed_image,
                                       lang='eng',
                                       config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789')
    #remove newline character and leading white space
    result = text.replace('\n','').lstrip()
    if field_value[3][0] == "with title":
        result = result[len(field_value[3][1]):]
    result = result.lstrip()
    return result

### radio_button_process function. input is page and value from pdf_structure dictionary
## the backgroud_mean is the mean of background for a 200 by 200 square. To check the 
## status of the box in comparison with background. Useful if page is noisy.
## if the box value is less than 90% of background it will be considered as selected
def radio_button_process (page, field_value, background_mean):
    result = None
    current_choice = background_mean-(background_mean//10)
    for index, option in enumerate(value[3]):
        cropped=page.crop(field_value[1][index])
        preprocessed_image = preprocess_image(cropped)
        box_mean = np.mean(preprocessed_image)
        if box_mean < current_choice:
            result = field_value[3][index]
            current_choice = box_mean
    return result

### check_box_process function. input is page and value from pdf_structure dictionary
## the backgroud_mean is the mean of background for a 200 by 200 square. To check the 
## status of the box in comparison with background. Useful if page is noisy.
## if the box value is less than 90% of background it will be considered as selected
# =============================================================================
# mean value for clean page:
#     radio_button (check mark) = 212
#     Check_box (black square) = 128
#     The weird student check box = 218
#     empty check box = 255
# =============================================================================
def check_box_process (page, field_value, background_mean):
    cropped=page.crop(field_value[1])
    preprocessed_image = preprocess_image(cropped)
    
    box_mean = np.mean(preprocessed_image)
    #calculating the check box mean value if it was blank
    result = field_value[3][1]
    if field_value[0] == "Student":
        if box_mean < 215:
            result = field_value[3][0]   
    else:
        if box_mean < background_mean-(background_mean//10):
            result = field_value[3][0]
    return result

def space_retainer ():
    return None

row = 0
mat = fitz.Matrix(500/72, 500/72)
for pdf_filename in glob.glob(f'{pdf_folder}*.pdf'):
    
    print (pdf_filename)
    
    df.at[row,'File Name'] = os.path.basename(pdf_filename)
    #pages = convert_from_path(pdf_filename, 500)
    doc = fitz.open(pdf_filename)  
    for page_number, page_structure in enumerate(pdf_structure.values()):
        ### since the PIL can not detect some of the checkmarks
        ### we load the page as pixamp png object then pass it to
        ### PIL Image as Object
        current_page = doc.loadPage(page_number)
        pixmap_current_page = current_page.getPixmap(matrix = mat)
        pixamp_object = pixmap_current_page.getImageData("PNG")
        page = Image.open(io.BytesIO(pixamp_object))
        #set a reference value for background
        background_picture = page.crop((2600,5200,2800,5400))
        background_mean = np.mean(preprocess_image(background_picture))
        #print ("page no: ", page_number)
        for key, value in page_structure.items():
            #print (key)
            if value[2]=="text box":
                df.at[row,value[0]] = text_box_process(page, value)
            if value[2]=="radio button":
                df.at[row,value[0]] = radio_button_process(page, value, background_mean)
            if value[2]=="check box":
                df.at[row,value[0]] = check_box_process(page, value, background_mean)
            if value[2]=="digit box":
                df.at[row,value[0]] = digit_box_process(page, value)
            if value[2]=="space retainer":
                df.at[row,value[0]] = space_retainer()
        address = f'{df.at[row,"contact_current_address"]}, '\
                  f'{df.at[row,"contact_city"]}, '\
                  f'{df.at[row,"contact_state"]}'  
        google_geo = Google_geocoder_address (gps_id = row,
                                              one_line_address = address)
        df.at[row,"contact_zip_code"] = google_geo.standard_address_zip_code_short
        df.at[row,"contact_lat"] = google_geo.lat
        df.at[row,"contact_long"] = google_geo.long
        census_geo = Census_geocoder_coordinate (gps_id = row,
                                                 long = google_geo.long,
                                                 lat = google_geo.lat
                                                )
        df.at[row,"contact_fips_code"] = census_geo.geo_id   
    row +=1

date_fields = ["date_of_symptom_onset",
               "date_of_last_symptom",
               "date_of_last_exposure",
               "date_interview_completed",
               "contact_date_of_birth"
              ]

def date_combine(month, day, year):
    date_string = f'{month}/{day}/{year}'
    try:
        result = datetime.datetime.strptime(date_string, "%m/%d/%Y").date()
    except:
        result = None
    return result

for date_field in date_fields:
    df[date_field] = df.apply(lambda x: date_combine(x[f'{date_field}_month'],
                                                     x[f'{date_field}_day'],
                                                     x[f'{date_field}_year']), axis=1)
# =============================================================================
# columns_to_drop = ["date_of_symptom_onset_month",
#                    "date_of_symptom_onset_day",
#                    "date_of_symptom_onset_year",
#                    "date_of_last_symptom_month",
#                    "date_of_last_symptom_day",
#                    "date_of_last_symptom_year",
#                    "date_of_last_exposure_month",
#                    "date_of_last_exposure_day",
#                    "date_of_last_exposure_year",
#                    "date_interview_completed_month",
#                    "date_interview_completed_day",
#                    "date_interview_completed_year",
#                    "contact_date_of_birth_month",
#                    "contact_date_of_birth_day",
#                    "contact_date_of_birth_year"
#                   ]
# df.drop(columns_to_drop, axis=1, inplace=True)        
# =============================================================================
df.to_csv(f'{output_folder}df.csv')

#value = pdf_structure["Page 1"][59]
#cropped=page.crop(value[1])
#preprocessed_image = preprocess_image(cropped)
#text = pytesseract.image_to_string(preprocessed_image, lang='eng',config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789')           
#print('empty',np.mean(preprocessed_image))            
#check_box_process(page, value, background_mean)

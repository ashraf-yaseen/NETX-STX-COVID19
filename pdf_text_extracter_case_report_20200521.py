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
pdf_folder = 'C:/Users/Yashar/Google Drive/UT HSC/Projects/COVID_19/PDFtoText/Case_report/'
### define the folder to save the results
output_folder = 'C:/Users/Yashar/Google Drive/UT HSC/Projects/COVID_19/PDFtoText/Case_report/'
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
pdf_structure = {"Page 1":{#1:["record_id", (), "text box", ["without title"]],
                           1:["case_id", (1940,490,2400,570), "text box",["without title"]],
                           2:["today_date", (615,490,1016,570), "text box", ["without title"]],
                           3:["patient_name", (293,668,1265,796), "text box", ["with title", "Patient's Name:"]],
                           4:["patient_date_of_birth", (293,800,1265,928), "text box", ["with title", "Date of Birth:"]],
                           5:["patient_address", (1270,668,2154,796), "text box", ["with title", "Address:"]],
                           6:["patient_city", (2160,668,2922,796), "text box", ["with title", "City:"]],
                           7:["patient_county", (2927,668,3510,796), "text box", ["with title", "County:"]],
                           8:["patient_state", (3514,668,3997,796), "text box", ["with title", "State:"]],
                           9:["patient_zip", (), "space retainer", ["without title"]],
                           10:["patient_lat",(), "space retainer", ["without title"]],
                           11:["patient_long",(), "space retainer", ["without title"]],
                           12:["patient_fips_code",(), "space retainer", ["without title"]],
                           13:["patient_home_phone", (1270,800,2154,928), "text box", ["with title", "Home Phone:"]],
                           14:["patient_cell_phone", (2160,800,2922,928), "text box", ["with title", "Cell Phone:"]],
                           15:["patient_email", (2927,800,3997,928), "text box", ["with title", "Email:"]],
                           16:["state_id", (293,1009,1248,1137), "text box", ["with title", "State ID:"]],
                           17:["date_of_report", (1252,1009,2154,1137), "text box", ["with title", "Date of Report:"]],
                           18:["report_city", (2160,1009,2919,1137), "text box", ["with title", "City:"]],
                           19:["report_city_county", (2923,1009,3500,1137), "text box", ["with title", "County:"]],
                           20:["report_state", (3504,1009,3997,1137), "text box", ["with title", "State:"]],
                           21:["investigator_name", (293,1149,1248,1269), "text box", ["with title", "Investigator's Name:"]],
                           22:["investigator_phone", (1252,1149,2154,1269), "text box", ["with title", "Phone:"]],
                           23:["investigator_email", (2160,1149,2919,1269), "text box", ["with title", "Email:"]],
                           24:["investigator_start_date", (2923,1149,3997,1269), "text box", ["with title", "Investigation Start Date:"]],
                           25:["physician_name", (293,1273,1248,1402), "text box", ["with title", "Physician's Name:"]],
                           26:["physician_phone", (1252,1273,3997,1402), "text box", ["with title", "Phone/Pager:"]],
                           27:["reporter_name", (293,1406,1248,1534), "text box", ["with title", "Reporter's Name:"]],
                           28:["reporter_phone", (1252,1406,2154,1534), "text box", ["with title", "Phone:"]],
                           29:["reporter_email", (2160,1406,3997,1534), "text box", ["with title", "Email:"]],
                           30:["sex", [(394,1759,429,1794),(558,1759,593,1794)], "radio button", [0,1]],
                           31:["age", (868,1740,1092,1805), "text box", ["without title"]],
                           32:["age_unit", [(1129,1759,1164,1794),(1291,1759,1326,1794)], "radio button", ["Year", "Month"]],
                           33:["residency", [(1805,1759,1840,1794),(2238,1759,2273,1794)], "radio button", [0, 1]],
                           34:["country", (2773,1736,4004,1805), "text box", ["with title", "Country:"]],
                           35:["race", [(428,1836,463,1871),(670,1836,705,1871),(892,1836,927,1871),(1118,1836,1153,1871),(1587,1836,1621,1871),(2316,1836,2351,1871),(2648,1836,2683,1871)],"radio button", [0,1,2,3,4,5,6]],
                           36:["race_other", (2688,1829,3774,1881), "text box", ["with title", "Other:"]],
                           37:["hispanic",[(523,1912,562,1951),(696,1912,735,1951),(858,1912,898,1951)],"radio button", [1,0,2]],
                           38:["Unemployed", (1777,1988,1812,2023), "check box", [1,0]],
                           39:["Student", (2299,1988,2318,2011), "check box", [1,0]],
                           40:["occupation", (248,1983,1704,2031), "text box", ["with title", "Occupation:"]],
                           41:["name_of_school", (2980,1940,3775,2030), "text box", ["without title"]],
                           42:["aymptomatic", (1742,2253,1781,2292), "check box", [1, 0]],
                           43:["symptom_onset", (941,2210,1672,2300), "text box", ["without title"]],
                           44:["fever", (260,2445,299,2484), "check box", [1,0]],
                           45:["cough", (577,2445,615,2484), "check box", [1,0]],
                           46:["sore_throat", (895,2445,934,2484), "check box", [1,0]],
                           47:["shortness_of_Breath", (1355,2445,1394,2484), "check box", [1,0]],
                           48:["chills", (260,2638,299,2677), "check box", [1,0]],
                           49:["headache", (546,2638,585,2677), "check box", [1,0]],
                           50:["muscle_ache", (965,2638,1004,2677), "check box", [1,0]],
                           51:["vomiting", (1484,2638,1523,2677), "check box", [1,0]],
                           52:["abdominal_pain", (1878,2638,1917,2677), "check box", [1,0]],
                           53:["diahrrea", (2462,2638,2501,2677), "check box", [1,0]],
                           54:["other", (2845,2638,2884,2677), "check box", [1,0]],
                           55:["other_symptoms", (3318,2618,3850,2687), "text box", ["without title"]],
                           56:["additional_symptoms_other", (3318,2618,3850,2687), "text box", ["without title"]],
                           57:["travel", [(3298,2925,3337,2964),(3470,2925,3509,2964),(3653,2925,3692,2964)], "radio button", [1,0,2]],
                           58:["travel1_destination", (566,3116,1480,3192), "text box", ["without title"]],
                           59:["travel1_date_arrived_month", (1631,3115,1769,3192), "digit box", ["without title"]],
                           60:["travel1_date_arrived_day", (1799,3115,1934,3192), "digit box", ["without title"]],
                           61:["travel1_date_arrived_year", (1962,3116,2139,3192), "digit box", ["without title"]],
                           62:["travel1_date_arrived", (), "space retainer", ["without title"]],
                           63:["travel1_date_left_month", (2587,3116,2763,3192), "digit box", ["without title"]],
                           64:["travel1_date_left_day", (2791,3116,2928,3192), "digit box", ["without title"]],
                           65:["travel1_date_left_year", (2955,3116,3167,3192), "digit box", ["without title"]],
                           66:["travel1_date_left", (), "space retainer", ["without title"]],
                           67:["travel2_destination", (566,3204,1480,3277), "text box", ["without title"]],
                           68:["travel2_date_arrived_month", (1631,3200,1767,3277), "digit box", ["without title"]],
                           69:["travel2_date_arrived_day", (1799,3204,1934,3277), "digit box", ["without title"]],
                           70:["travel2_date_arrived_year", (1962,3204,2139,3277), "digit box", ["without title"]],
                           71:["travel2_date_arrived", (), "space retainer", ["without title"]],
                           72:["travel2_date_left_month", (2587,3204,2763,3277), "digit box", ["without title"]],
                           73:["travel2_date_left_day", (2791,3204,2928,3277), "digit box", ["without title"]],
                           74:["travel2_date_left_year", (2955,3204,3167,3277), "digit box", ["without title"]],
                           75:["travel2_date_left", (), "space retainer", ["without title"]],
                           76:["travel3_destination", (566,3299,1480,3361), "text box", ["without title"]],
                           77:["travel3_date_arrived_month", (1631,3299,1769,3361), "digit box", ["without title"]],
                           78:["travel3_date_arrived_day", (1799,3299,1934,3361), "digit box", ["without title"]],
                           79:["travel3_date_arrived_year", (1962,3299,2139,3361), "digit box", ["without title"]],
                           80:["travel3_date_arrived", (), "space retainer", ["without title"]],
                           81:["travel3_date_left_month", (2587,3299,2763,3361), "digit box", ["without title"]],
                           82:["travel3_date_left_day", (2791,3299,2928,3361), "digit box", ["without title"]],
                           83:["travel3_date_left_year", (2955,3299,3167,3361), "digit box", ["without title"]],
                           84:["travel3_date_left", (), "space retainer", ["without title"]],
                           85:["close_contact_investigation", [(3298,3603,3337,3642),(3470,3603,3509,3642),(3653,3603,3692,3642)], "radio button", [1,0,2]],
                           86:["close_contact_lab", [(3298,3701,3337,3740),(3470,3701,3509,3740),(3653,3701,3692,3740)], "radio button", [1,0,2]],
                           87:["contact_ill", [(3298,3794,3337,3833),(3470,3794,3509,3833),(3653,3794,3692,3833)], "radio button", [1,0,2]],
                           88:["us_case", [(3298,3888,3337,3927),(3470,3888,3509,3927),(3653,3888,3692,3927)], "radio button", [1,0,2]],
                           89:["intenational_case", [(3298,3982,3337,4021),(3470,3982,3509,4021),(3653,3982,3692,4021)], "radio button", [1,0,2]],
                           90:["country_diagnosed", (320,4100,1365,4167), "text box", ["without title"]],
                           91:["no_known_exposure", [(3298,4213,3337,4252),(3470,4213,3509,4252),(3653,4213,3692,4252)], "radio button", [1,0,2]],
                           92:["healthcare_worker", [(1319,4757,1358,4796),(1491,4757,1530,4796),(1674,4757,1713,4796)], "radio button", [1,0,2]],
                           93:["hist_healthcare_facility", [(2540,4858,2579,4897),(2711,4858,2750,4897),(2894,4858,2933,4897)], "radio button", [1,0,2]]
                           },
                   "Page 2":{1:["provide_care", [(1400,531,1439,570),(1572,531,1611,570),(1755,531,1794,570)], "radio button", [1,0,2]],
                           2:["member_of_cluster", [(2569,723,2610,765),(2741,723,2780,762),(2924,723,2963,762)], "radio button", [1,0,2]],
                           3:["diagnosis_pneumonia", [(2162,824,2201,863),(2303,824,2342,863)], "radio button", [1,0]],
                           4:["diagnosis_ards", [(3540,824,3579,863),(3680,824,3719,863)], "radio button", [1,0]],
                           5:["none_comorbidity", (1549,925,1588,964), "check box", [1,0]],
                           6:["unknown_comorbidity", (1824,925,1863,964), "check box", [1,0]],
                           7:["pregnant_comorbidity", (2236,925,2275,964), "check box", [1,0]],
                           8:["diabetes_comorbidity", (2599,925,2638,964), "check box", [1,0]],
                           9:["cardiac_disease_comborbidity", (2954,925,2993,964), "check box", [1,0]],
                           10:["hypertension_comorbidity", (3495,925,3534,964), "check box", [1,0]],
                           11:["chronic_pulmonary_comorbidity", (260,1026,299,1065), "check box", [1,0]],
                           12:["chronic_kidney_comorbidity", (1177,1026,1216,1065), "check box", [1,0]],
                           13:["chronic_liver_comorbidity", (1974,1026,2013,1065), "check box", [1,0]],
                           14:["immunocompromised_comorbidity", (2707,1026,2746,1065), "check box", [1,0]],
                           15:["other_specify_comorbidity", (3472,1026,3511,1065), "check box", [1,0]],
                           16:["hospitalized", [(1225,1126,1266,1165),(2172,1126,2214,1165)], "radio button", [1,0]],
                           17:["admit_date", (1665,1094,2114,1177), "text box", ["without title"]],
                           18:["admitted_icu", [(2884,1126,2923,1165),(3057,1126,3096,1165)], "radio button", [1,0]],
                           19:["icu_admit_date", (3875,1094,4145,1177), "text box", ["without title"]],
                           20:["intubated", [(635,1227,674,1266),(775,1227,815,1266),(926,1227,965,1266)], "radio button", [1,0,2]],
                           21:["ecmo", [(1503,1227,1542,1266),(1644,1227,1683,1266),(1796,1227,1835,1266)], "radio button", [1,0,2]],
                           22:["patient_died", [(2431,1227,2470,1266),(2602,1226,2641,1266)], "radio button", [1,0]],
                           23:["date_of_death_month", (3365,1200,3451,1278), "digit box", ["without title"]],
                           24:["date_of_death_day", (3479,1200,3548,1278), "digit box", ["without title"]],
                           25:["date_of_death_year", (3575,1200,3714,1278), "digit box", ["without title"]],
                           26:["date_of_death", (), "space retainer", ["without title"]],
                           27:["discharged_hospital", [(1034,1328,1073,1367),(1897,1328,1936,1367)], "radio button", [1,0]],
                           28:["discharge_date", (1388,1298,1840,1379), "text box", ["without title"]],
                           29:["isolated_at_home", [(3060,1328,3099,1367),(3232,1328,3271,1367)], "radio button", [1,0]],
                           30:["other_diagnosis_etiology", [(2552,1429,2591,1468),(3412,1429,3451,1468),(3595,1429,3634,1468)], "radio button", [1,0,2]],
                           31:["other_diagnosis_etiology_specify", (2885,1405,3370,1480), "text box", ["without title"]],
                           32:["additional_comments", (254,1503,3997,2326), "text box", ["with title", "Additional Comments (smoking status, other comorbidities, potential contacts/places of exposure, etc.):"]],
                           33:["where_testing_occur", [(1417,2453,1456,2492),(1417,2553,1456,2592),(1417,2654,1456,2693)], "radio button", [0,1,2]],
                           34:["commercial_specify", (2805,2406,3439,2502), "text box", ["without title"]],
                           35:["dshs_lab_specify", (3510,2520,4004,2602), "text box", ["without title"]],
                           36:["flu_rapid_ag_type", [(850,3027,885,3062),(969,3027,1004,3062)], "radio button",[0,1]],
                           37:["flu_rapid_ag", [(1214,3030,1253,3069),(1401,3030,1440,3069),(1620,3030,1659,3069),(1917,3030,1956,3069)], "radio button",[0,1,2,3]],
                           38:["flu_pcr_type", [(853,3122,888,3158),(971,3122,1006,3157)], "radio button",[0,1]],
                           39:["flu_pcr", [(1214,3126,1253,3165),(1401,3126,1440,3165),(1620,3126,1659,3165),(1917,3126,1956,3165)], "radio button",[0,1,2,3]],
                           40:["rsv", [(1214,3222,1253,3261),(1401,3222,1440,3261),(1620,3222,1659,3261),(1917,3222,1956,3261)], "radio button",[0,1,2,3]],
                           41:["h_metapneumovirus", [(1214,3318,1253,3357),(1401,3318,1440,3357),(1620,3318,1659,3357),(1917,3318,1956,3357)], "radio button",[0,1,2,3]],
                           42:["parainfluenza1_4", [(1214,3413,1253,3452),(1401,3413,1440,3452),(1620,3413,1659,3452),(1917,3413,1956,3452)], "radio button",[0,1,2,3]],
                           43:["adenovirus", [(1214,3509,1253,3548),(1401,3509,1440,3548),(1620,3509,1659,3548),(1917,3509,1956,3548)], "radio button",[0,1,2,3]],
                           44:["rhinovirus_enterovirus", [(3214,3030,3253,3069),(3401,3030,3440,3069),(3620,3030,3659,3069),(3917,3030,3956,3069)], "radio button",[0,1,2,3]],
                           45:["coronovirus_oc43_229e_hku1_nl63", [(3214,3126,3253,3165),(3401,3126,3440,3165),(3620,3126,3659,3165),(3917,3126,3956,3165)], "radio button",[0,1,2,3]],
                           46:["m_pneumoniae", [(3214,3282,3253,3321),(3401,3282,3440,3321),(3620,3282,3659,3321),(3917,3282,3956,3321)], "radio button",[0,1,2,3]],
                           47:["c_pneumoniae", [(3214,3378,3253,3417),(3401,3378,3440,3417),(3620,3378,3659,3417),(3917,3378,3956,3417)], "radio button",[0,1,2,3]],
                           48:["rdr_other", [(3214,3473,3253,3512),(3401,3473,3440,3512),(3620,3473,3659,3512),(3917,3473,3956,3512)], "radio button",[0,1,2,3]],
                           49:["rdr_other_specify", (2684,3450,2973,3508), "text box", ["without title"]],
                           50:["np_swab_comm_ph", [(3417,3971,3456,4010),(3840,3971,3879,4010)], "radio button", [0,1]],
                           51:["np_swab_specimen_id", (923,3940,1421,4032), "text box", ["without title"]],
                           52:["np_swab_date_collected", (1425,3940,1859,4032), "text box", ["without title"]],
                           53:["np_swab_date_resulted", (1863,3940,2328,4032), "text box", ["without title"]],
                           54:["np_swab_lab_name", (2332,3940,3232,4032), "text box", ["without title"]],
                           55:["op_swab_comm_ph", [(3417,4067,3456,4106),(3840,4067,3879,4106)], "radio button", [0,1]],
                           56:["op_swab_specimen_id", (923,4036,1421,4128), "text box", ["without title"]],
                           57:["op_swab_date_collected", (1425,4036,1859,4128), "text box", ["without title"]],
                           58:["op_swab_date_resulted", (1863,4036,2328,4128), "text box", ["without title"]],
                           59:["op_swab_lab_name", (2332,4036,3232,4128), "text box", ["without title"]],
                           60:["sputum_comm_ph", (3417,4163,3456,4202),(3840,4163,3879,4202), "radio button", [0,1]],
                           61:["sputum_specimen_id", (923,4132,1421,4224), "text box", ["without title"]],
                           62:["sputum_date_collected", (1425,4132,1859,4224), "text box", ["without title"]],
                           63:["sputum_date_resulted", (1863,4132,2328,4224), "text box", ["without title"]],
                           64:["sputum_lab_name", (2332,4132,3232,4224), "text box", ["without title"]],
                           65:["bal_fluid_comm_ph", [(3417,4259,3456,4298),(3840,4259,3879,4298)], "radio button", [0,1]],
                           66:["bal_fluid_specimen_id", (923,4228,1421,4320), "text box", ["without title"]],
                           67:["bal_fluid_date_collected", (1425,4228,1859,4320), "text box", ["without title"]],
                           68:["bal_fluid_date_resulted", (1863,4228,2328,4320), "text box", ["without title"]],
                           69:["bal_fluid_lab_name", (2332,4228,3232,4320), "text box", ["without title"]],
                           70:["tracheal_aspirate_comm_ph", [(3417,4355,3456,4394),(3840,3355,3879,4394)], "radio button", [0,1]],
                           71:["tracheal_aspirate_specimen_id", (923,4324,1421,4416), "text box", ["without title"]],
                           72:["tracheal_aspirate_date_collected", (1425,4324,1859,4416), "text box", ["without title"]],
                           73:["tracheal_aspirate_date_resulted", (1863,4324,2328,4416), "text box", ["without title"]],
                           74:["tracheal_aspirate_lab_name", (2332,4324,3232,4416), "text box", ["without title"]],
                           75:["stool_comm_ph", [(3417,4450,3456,4489),(3840,4450,3879,4489)], "radio button", [0,1]],
                           76:["stool_specimen_id", (923,4420,1421,4511), "text box", ["without title"]],
                           77:["stool_date_collected", (1425,4420,1859,4511), "text box", ["without title"]],
                           78:["stool_date_resulted", (1863,4420,2328,4511), "text box", ["without title"]],
                           79:["stool_lab_name", (2332,4420,3232,4511), "text box", ["without title"]],
                           80:["postmortem_comm_ph", [(3417,4546,3456,4585),(3840,4546,3879,4585)], "radio button", [0,1]],
                           81:["postmortem_specimen_id", (923,4516,1421,4667), "text box", ["without title"]],
                           82:["postmortem_date_collected", (1425,4516,1859,4667), "text box", ["without title"]],
                           83:["postmortem_date_resulted", (1863,4516,2328,4667), "text box", ["without title"]],
                           84:["postmortem_lab_name", (2332,4516,3232,4667), "text box", ["without title"]],
                           85:["postmortem_specimen_specify", (300,4516,919,4667),"text box", ["with title", "Postmortem Specify:"]]
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
        address = f'{df.at[row,"patient_address"]}, '\
                  f'{df.at[row,"patient_city"]}, '\
                  f'{df.at[row,"patient_state"]}'  
        google_geo = Google_geocoder_address (gps_id = row,
                                              one_line_address = address)
        df.at[row,"patient_zip"] = google_geo.standard_address_zip_code_short
        df.at[row,"patient_lat"] = google_geo.lat
        df.at[row,"patient_long"] = google_geo.long
        census_geo = Census_geocoder_coordinate (gps_id = row,
                                                 long = google_geo.long,
                                                 lat = google_geo.lat
                                                )
        df.at[row,"patient_fips_code"] = census_geo.geo_id   
    row +=1

date_fields = ["travel1_date_arrived",
               "travel1_date_left",
               "travel2_date_arrived",
               "travel2_date_left",
               "travel3_date_arrived",
               "travel3_date_left",
               "date_of_death"
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
#t = current_page.getPixmap(matrix = mat, clip=(2600,5200,2800,5400))
#pix = page.getPixmap(matrix = mat)
#t = page.getImageData("PNG")

#t1= Image.open(io.BytesIO(t))
#background_picture = t1.crop((2600,5200,2800,5400))
# pix.writePNG(f'{output_folder}t.png')
# -*- coding: utf-8 -*-
"""
Created on Mon August 10 11:13:20 2020
Working version May 21 2020
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
pdf_folder = '/Users/isela/Desktop/Form_Extraction/PDF_CR/NETHealth/Forms/'
### define the folder to save the results
output_folder = '/Users/isela/Desktop/Form_Extraction/PDF_CR/NETHealth/Forms/Output/'
### define the path to tessaract.exe that will be used by pytessaract (OCR)
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


#### pdf2image method ####
# =============================================================================
#pages = convert_from_path(f'{pdf_folder}FINAL_COVID-19 Case Report Form WAYLON ATTAWAY.pdf',
#                          dpi=500, grayscale=True)
#i = 1
#for page in pages:
#    page.save(f'{output_folder}{i}.jpg', 'JPEG')
#    i+=1
#pages = convert_from_bytes(open(r'/Users/Robotnic/Desktop/companyprofile.pdf','rb').read())
# =============================================================================

#### fitz method ####
# =============================================================================
#doc = fitz.open(f'{pdf_folder}DSHS-COVID19CaseReportForm_Apr022020.pdf')
#page = doc.loadPage(2) #number of page
#mat = fitz.Matrix(500/72, 500/72)
#pix = page.getPixmap(matrix = mat)
#pix.writePNG(f'{output_folder}t.png')
# =============================================================================


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

#Version (6/9/20 & 6/12/20)

pdf_structure = {"Page 1":{ 1:["today_date", (624,885,992,956), "text box", ["without title"]],
                            2:["case_id", (2539,885,3204, 956), "text box", ["without title"]],
                            3:["confirmed_type", (574,1008,613,1046),"check box", [1,0]],
                            4:["probable_type", (1010,1008,1050,1046), "check box", [1,0]],
                            5:["collected_patient_interview", (2729,1008,2769,1046), "check box", [1,0]],
                            6:["collected_medical_records",(3370,1008,3409,1046), "check box", [1,0]],
                            7:["first_name",(293,1157,1435,1285), "text box", ["with title", "Patient's Name; First:"]],
                            8:["middle_name",(1440,1157,2185,1285), "text box", ["with title", "Middle:"]],
                            9:["last_name", (2189,1157,3374,1285), "text box",["with title", "Last:"]],
                            10:["suffix_name", (3377,1157,3998,1285), "text box", ["with title", "Suffix:"]],
                            11:["patient_address", (293,1288,1749,1417), "text box", ["with title","Address:"]],
                            12:["patient_city", (1752,1288,2403,1417),"text box", ["with title", "City:"]],
                            13:["patient_county", (2409,1288,3030,1417), "text box", ["with title", "County:"]],
                            14:["patient_state", (3034,1288,3373,1417), "text box", ["with title", "State:"]],
                            15:["patient_zip", (3377,1288,3997,1417), "text box", ["with title", "Zip Code:"]],
                            16:["patient_lat",(), "space retainer", ["without title"]],
                            17:["patient_long",(), "space retainer", ["without title"]],
                            18:["patient_fips_code",(), "space retainer", ["without title"]],
                            19:["patient_date_of_birth", (293,1421,1435,1550), "text box",["with title", "Date of Birth: (MM/DD/YYYY)"]],
                            20:["patient_home_phone", (1440,1421,2092,1550), "text box", ["with title", "Home Phone:"]],
                            21:["patient_cell_phone", (2097,1421,2748,1550), "text box", ["with title", "Cell Phone:"]],
                            22:["patient_email", (2753,1421,3997,1550), "text box", ["with title", "Email:"]],
                            23:["state_id", (293,1624,1247,1752), "text box", ["with title", "STATE ID:"]],
                            24:["date_of_report", (1253,1624,2155,1752), "text box", ["with title", "Date of Report:"]],
                            25:["report_city", (2159,1624,2919,1752), "text box", ["with title", "City:"]],
                            26:["report_city_county", (2924,1624,3500,1752), "text box", ["with title", "County:"]],
                            27:["report_state", (3505,1624,3997,1752), "text box", ["with title", "State:"]],
                            28:["investigator_name", (293,1757,1248,1884), "text box", ["with title", "Investigator's name:"]],
                            29:["investigator_phone", (1252,1757,2154,1884), "text box", ["with title", "Phone:"]],
                            30:["investigator_email", (2160,1757,2918,1884), "text box", ["with title", "Email:"]],
                            31:["investigator_start_date", (2923,1757,3997,1884), "text box", ["with title", "Investigation Start Date:"]],
                            32:["physician_name", (293,1889,1248,2017), "text box", ["with title", "Physician's name:"]],
                            33:["physician_phone", (1252,1889,3997,2017), "text box", ["with title", "Phone/Pager:"]],
                            34:["reporter_name", (293,2021,1248,2150), "text box", ["with title", "Reporter's Name:"]],
                            35:["reporter_phone", (1252,2021,2154,2149), "text box", ["with title", "Phone:"]],
                            36:["reporter_email", (2160,2021,3997,2149), "text box", ["with title", "Email:"]],
                            37:["sex", [(397,2361,436,2400),(569,2361,609,2400)], "radio button", [0,1]],
                            38:["age", (887,2353,1109,2410), "text box", ["without title"]],
                            39:["age_unit", [(1148,2361,1188,2400),(1318,2361,1357,2400)], "radio button", ["Year", "Month"]],
                            40:["race", [(449,2455,488,2492),(699,2455,739,2492),(932,2455,971,2492),(1197,2455,1233,2492),(1699,2455,1738,2492),(2605,2455,2645,2492),(2980,2455,3020,2492)],"radio button", [0,1,2,3,4,5,6]],
                            41:["race_other", (3222,2433,3974,2503), "text box", ["without title"]],
                            42:["hispanic",[(829,2544,869,2582),(1011,2544,1051,2582),(1261,2544,1300,2582)], "radio button", [1,0,2]],
                            43:["residency", [(2068,2544,2108,2582),(2510,2544,2550,2582)], "radio button", [0, 1]],
                            44:["country", (3272,2516,4000,2592), "text box", ["without title"]],
                            45:["exposure_residence_type", [(759,2826,795,2862),(1353,2826,1389,2862),(1760,2826,1794,2862),(2416,2826,2452,2862),
                                                             (3166,2826,3201,2862),(260,2919,294,2954),(1009,2919,1044,2954),(1759,2919,1795,2954),
                                                             (2259,2919,2295,2954),(3260,2919,3294,2954),(259,3011,294,3046),(1355,3011,1390,3046),
                                                             (1760,3011,1794,3046),(2105,3011,2140,3046),(2509,3011,2545,3046),(3259,3011,3295,3046),
                                                             (259,3103,294,3139)], "radio button", [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]],
                            46:["other_residence_type", (879,3067,1728,3149), "text box",["without title"]],
                            47:["facility_name", (3215,3065,4001,3149), "text box",["without title"]],
                            48:["occupation", (569,3167,1698,3240), "text box", ["without title"]],
                            49:["Unemployed", (1854,3197,1889,3232), "check box", [1,0]],
                            50:["Student", (2385,3197,2419,3232), "check box", [1,0]],
                            51:["name_of_school", (3111,3165,4001,3241), "text box", ["without title"]],
                            52:["contact_case_conf_prob", [(3295,3374,3331,3408),(3451,3374,3487,3408),(3615,3374,3651,3408)], "radio button", [1,0,2]],
                            53:["contact_ill", [(3295,3466,3331,3500),(3451,3466,3487,3500),(3615,3466,3651,3500)], "radio button", [1,0,2]],
                            54:["us_case", [(3295,3558,3331,3593),(3451,3558,3487,3593),(3615,3558,3651,3593)], "radio button", [1,0,2]],
                            55:["intenational_case", [(3295,3650,3331,3685),(3451,3650,3487,3685),(3615,3650,3651,3685)], "radio button", [1,0,2]],
                            56:["country_diagnosed", (2042,3671,2981,3747), "text box", ["without title"]],
                            57:["no_known_exposure", [(3295,3792,3330,3827),(3451,3792,3487,3827),(3616,3792,3650,3827)], "radio button", [1,0,2]],
                            58:["travel", [(3297,4129,3332,4163),(3453,4129,3488,4163),(3618,4129,3653,4163)], "radio button", [1,0,2]],
                            59:["travel1_destination", (515,4270,2149,4345), "text box", ["without title"]],
                            60:["travel1_date_arrived", (2502,4270,3045,4345), "text box", ["without title"]],
                            61:["travel1_date_left", (3313,4270,3859,4345), "text box", ["without title"]],
                            62:["travel2_destination", (522,4370,2150,4444), "text box", ["without title"]],
                            63:["travel2_date_arrived", (2507,4370,3041,4444), "text box", ["without title"]],
                            64:["travel2_date_left", (3324,4370,3858,4444), "text box", ["without title"]],
                            65:["travel3_destination", (517,4475,2149,4566), "text box", ["without title"]],
                            66:["travel3_date_arrived", (2503,4475,3040,4566), "text box", ["without title"]],
                            67:["travel3_date_left", (3320,4475,3859,4566), "text box", ["without title"]],
                            68:["form_version",(239,5167,1344,5247),"text box",["with title","Version"]]
                            },
                 "Page 2":{ 1:["healthcare_worker", [(1212,528,1247,563),(1367,528,1402,563),(1532,527,1568,563)], "radio button", [1,0,2]],
                            2:["provide_care", [(1286,618,1320,654),(1440,618,1476,654),(1605,618,1640,654)], "radio button", [1,0,2]],
                            3:["member_of_cluster", [(1852,793,1887,827),(2007,793,2042,827),(2172,793,2207,828)], "radio button", [1,0,2]],
                            4:["outbreak_case", [(1409,884,1444,918),(1541,884,1576,918),(1698,884,1733,918)], "radio button", [1,0,2]],
                            5:["outbreak_name", (2855,861,3970,929), "text box", ["without title"]],
                            6:["outbreak_name_pt2", (249,945,3970,1012), "text box", ["without title"]],
                            7:["symptom_onset", (868,1233,1528,1305), "text box", ["without title"]],
                            8:["aymptomatic", (1867,1262,1903,1296), "check box", [1, 0]],
                            9:["illness_end_date",(2948,1240,3607,1305), "text box",["without title"]],
                            10:["fever", (259,1437,295,1473), "check box", [1,0]],
                            11:["temp_F",(1331,1414,1491,1485),"text box", ["without title"]],
                            12:["cough", (1697,1437,1731,1473), "check box", [1,0]],
                            13:["sore_throat", (2073,1437,2108,1473), "check box", [1,0]],
                            14:["shortness_of_Breath", (2572,1437,2607,1473), "check box", [1,0]],
                            15:["chills", (3292,1437,3327,1473), "check box", [1,0]],
                            16:["headache", (3635,1437,3670,1473), "check box", [1,0]],
                            17:["muscle_ache", (260,1530,294,1565), "check box", [1,0]],
                            18:["vomiting", (792,1530,826,1565), "check box", [1,0]],
                            19:["abdominal_pain", (1228,1530,1263,1565), "check box", [1,0]],
                            20:["diahrrea", (1822,1530,1857,1565), "check box", [1,0]],
                            21:["loss_taste_smell",(2259,1530,2294,1565),"check box",[1,0]],
                            22:["loss_appetite",(3447,1530,3483,1565),"check box", [1,0]],
                            23:["fatigue",(259,1624,294,1659),"check box",[1,0]],
                            24:["runny_nose",(884,1624,920,1659),"check box", [1,0]],
                            25:["wheezing",(1416,1624,1451,1659),"check box", [1,0]],
                            26:["chest_pain",(1884,1624,1919,1659),"check box",[1,0]],
                            27:["other", (2353,1624,2389,1659), "check box", [1,0]],
                            28:["other_symptoms", (2795,1591,4001,1669), "text box", ["without title"]],
                            29:["none_comorbidity", (1509,1716,1545,1751), "check box", [1,0]],
                            30:["unknown_comorbidity", (1822,1716,1858,1751), "check box", [1,0]],
                            31:["pregnant_comorbidity", (2260,1716,2294,1751), "check box", [1,0]],
                            32:["due_date", (2839,1693,3190,1762), "text box", ["without title"]],
                            33:["diabetes_comorbidity", (3417,1716,3452,1751), "check box", [1,0]],
                            34:["cardiac_disease_comborbidity", (259,1808,295,1842), "check box", [1,0]],
                            35:["hypertension_comorbidity", (822,1808,858,1842), "check box", [1,0]],
                            36:["chronic_pulmonary_comorbidity", (1323,1808,1358,1842), "check box", [1,0]],
                            37:["chronic_kidney_comorbidity", (2260,1808,2295,1842), "check box", [1,0]],
                            38:["chronic_liver_comorbidity", (3010,1808,3044,1842), "check box", [1,0]],
                            39:["immunocompromised_comorbidity", (259,1900,294,1936), "check box", [1,0]],
                            40:["asthma",(1229,1900,1265,1936),"check box", [1,0]],
                            41:["hemoglobin_disorders",(1666,1900,1701,1936), "check box", [1,0]],
                            42:["severe_obesity",(259,1992,294,2028),"check box",[1,0]],
                            43:["other_specify_comorbidity", (1229,1992,1263,2028), "check box", [1,0]],
                            44:["other_text_comorbidity",(1666,1957,4000,2039),"text box",["without title"]],
                            45:["hospitalized", [(1127,2085,1162,2121),(3336,2085,3372,2121)], "radio button", [1,0]],
                            46:["hospital_name",(1613,2062,2609,2132),"text box",["without title"]],
                            47:["admit_date", (2918,2059,3314,2132), "text box", ["without title"]],
                            48:["discharged_hospital", [(952,2178,988,2213),(1898,2178,1934,2213)], "radio button", [1,0]],
                            49:["discharge_date", (1525,2151,1876,2224), "text box", ["without title"]],
                            50:["admitted_icu", [(737,2270,771,2305),(1854,2270,1888,2305)], "radio button", [1,0]],
                            51:["icu_admit_date", (1430,2247,1813,2317), "text box", ["without title"]],
                            52:["intubated", [(2371,2271,2406,2305),(2509,2271,2545,2305),(2667,2271,2702,2305)], "radio button", [1,0,2]],
                            53:["ecmo", [(3381,2271,3416,2305),(3509,2271,3544,2305),(3666,2271,3701,2305)], "radio button", [1,0,2]],
                            54:["mechanical_ventilation",[(982,2363,1017,2398),(1134,2363,1169,2398),(1292,2363,1327,2398)],"radio button", [1,0,2]],
                            55:["number_days_ventilator", (2770,2327,3056,2409),"text box", ["without title"]],
                            56:["diagnosis_pneumonia", [(1181,2540,1216,2574),(1353,2540,1388,2574)], "radio button", [1,0]],
                            57:["diagnosis_ards", [(2822,2540,2857,2574),(3010,2540,3045,2574)], "radio button", [1,0]],
                            58:["abnormal_chest_xray",[(856,2632,891,2668),(1010,2632,1044,2668),(1197,2632,1233,2668)], "radio button",[1,0,2]],
                            59:["abnormal_EKG",[(2233,2632,2268,2668),(2385,2632,2420,2668),(2573,2632,2607,2668)],"radio button",[1,0,2]],
                            60:["patient_died", [(632,2724,667,2760),(787,2724,823,2760)], "radio button", [1,0]],
                            61:["date_of_death", (1489,2690,1939,2771), "text box", ["without title"]],
                            62:["other_diagnosis_etiology", [(2322,2818,2358,2853),(3509,2818,3545,2853),(3675,2818,3710,2853)], "radio button", [1,0,2]],
                            63:["other_diagnosis_etiology_specify", (2624,2781,3492,2863), "text box", ["without title"]],
                            64:["isolated_at_home", [(1127,2910,1162,2945),(1283,2910,1318,2945)], "radio button", [1,0]],
                            65:["additional_comments", (253,3055,3998,3687), "text box", ["with title", "Additional Comments (smoking status, other comorbidities, potential contacts/places of exposure, etc.):"]],
                            66:["flu_rapid_ag_type", [(803,4149,843,4189),(960,4149,998,4189)], "radio button",[0,1]],
                            67:["flu_rapid_ag", [(1167,4149,1206,4189),(1355,4149,1395,4189),(1589,4149,1629,4189),(1824,4149,1864,4189)], "radio button",[0,1,2,3]],
                            68:["flu_pcr_type", [(804,4240,844,4278),(959,4240,999,4278)], "radio button",[0,1]],
                            69:["flu_pcr", [(1167,4240,1206,4278),(1355,4240,1395,4278),(1589,4240,1629,4278),(1824,4240,1864,4278)], "radio button",[0,1,2,3]],
                            70:["rsv", [(1167,4330,1206,4369),(1355,4330,1395,4369),(1589,4330,1629,4369),(1824,4330,1864,4369)], "radio button",[0,1,2,3]],
                            71:["h_metapneumovirus", [(1167,4420,1206,4459),(1355,4420,1395,4459),(1589,4420,1629,4459),(1824,4420,1864,4459)], "radio button",[0,1,2,3]],
                            72:["parainfluenza1_4", [(1167,4511,1206,4549),(1355,4511,1395,4549),(1589,4511,1629,4549),(1824,4511,1864,4549)], "radio button",[0,1,2,3]],
                            73:["adenovirus", [(1167,4601,1206,4639),(1355,4601,1395,4639),(1589,4601,1629,4639),(1824,4601,1864,4639)], "radio button",[0,1,2,3]],
                            74:["rhinovirus_enterovirus", [(3199,4149,3239,4188),(3387,4149,3427,4188),(3619,4149,3660,4188),(3870,4149,3910,4188)], "radio button",[0,1,2,3]],
                            75:["coronovirus_oc43_229e_hku1_nl63", [(3199,4240,3239,4278),(3387,4240,3427,4278),(3619,4240,3660,4278),(3870,4240,3910,4278)], "radio button",[0,1,2,3]],
                            76:["m_pneumoniae", [(3199,4330,3239,4369),(3387,4330,3427,4369),(3619,4330,3660,4369),(3870,4330,3910,4369)], "radio button",[0,1,2,3]],
                            77:["c_pneumoniae", [(3199,4421,3239,4459),(3387,4421,3427,4459),(3619,4421,3660,4459),(3870,4421,3910,4459)], "radio button",[0,1,2,3]],
                            78:["rdr_other", [(3199,4511,3239,4550),(3387,4511,3427,4550),(3619,4511,3660,4550),(3870,4511,3910,4550)], "radio button",[0,1,2,3]],
                            79:["rdr_other_specify", (2448,4488,3184,4573), "text box", ["without title"]]
                            },
                 "Page 3":{ 1:["1_covid_test_type", [(283,774,317,810),(283,849,317,885),(349,925,384,960),(349,1002,384,1037),
                                                       (349,1078,384,1113),(283,1152,317,1188),(283,1228,317,1263),(283,1312,317,1347)], "radio button", [1,2,3,4,5,6,7,8]],
                            2:["1_covid_test_type_other",(251,1366,775,1891),"text box",["without title"]],
                            3:["1_covid_specimen_type",[(805,782,840,817),(805,865,840,901),(805,950,840,985),(805,1034,840,1069),(805,1119,840,1153),
                                                            (805,1278,840,1314),(805,1364,840,1398),(805,1448,840,1482),(805,1684,840,1718)],"radio button",[1,2,3,4,5,6,7,8,9]],
                            4:["1_covid_specimen_type_other",(796,1577,1231,1646),"text box",["without title"]],
                            5:["1_covid_specimen_type_postmortem",(793,1736,1231,1806),"text box",["without title"]],
                            6:["1_covid_specimen_id",(1310,754,1806,1891),"text box",["without title"]],
                            7:["1_covid_test_result",[(1843,782,1878,816),(1843,865,1878,901),(1843,949,1878,984),(1843,1034,1878,1069)],"radio button", [1,2,3,4]],
                            8:["1_covid_test_date_collected",(2311,755,2645,1892),"text box",["without title"]],
                            9:["1_covid_test_date_resulted",(2650,754,2994,1892),"text box",["without title"]],
                            10:["1_covid_lab_type",[(3012,782,3047,816),(3012,942,3047,977)],"radio button",[1,2]],
                            11:["1_covid_lab_name",(3456,754,3994,1892),"text box",["without title"]],
                            12:["2_covid_test_type", [(283,1917,317,1952),(283,1992,317,2027),(350,2068,385,2103),(350,2145,384,2179),
                                                       (350,2220,384,2255),(283,2296,317,2331),(283,2372,317,2407),(283,2454,317,2488)], "radio button", [1,2,3,4,5,6,7,8]],
                            13:["2_covid_test_type_other",(250,2508,774,3035),"text box",["without title"]],
                            14:["2_covid_specimen_type",[(805,1924,840,1959),(805,2008,840,2042),(805,2093,840,2128),(805,2281,840,2296),(805,2177,840,2212),
                                                            (805,2422,840,2457),(805,2506,840,2540),(805,2589,840,2624),(805,2828,840,2862),],"radio button",[1,2,3,4,5,6,7,8,9]],
                            15:["2_covid_specimen_type_postmortem",(788,2720,1285,2786),"text box",["without title"]],
                            16:["2_covid_specimen_type_other",(784,2877,1276,2946),"text box",["without title"]],
                            17:["2_covid_specimen_id",(1311,1897,1806,2035),"text box",["without title"]],
                            18:["2_covid_test_result",[(1842,1923,1877,1959),(1842,2007,1877,2043),(1842,2092,1877,2127),(1842,2177,1877,2212)],"radio button", [1,2,3,4]],
                            19:["2_covid_test_date_collected",(2311,1897,2645,3034),"text box",["without title"]],
                            20:["2_covid_test_date_resulted",(2650,1896,2993,3035),"text box",["without title"]],
                            21:["2_covid_lab_type",[(3012,1923,3048,1958),(3012,2084,3048,2120)],"radio button",[1,2]],
                            22:["2_covid_lab_name",(3457,1897,3994,3035),"text box",["without title"]],
                            23:["3_covid_test_type", [(283,3060,317,3096),(283,3137,317,3171),(350,3212,384,3246),(350,3288,384,3322),
                                                         (350,3362,384,3397),(283,3439,317,3474),(283,3514,317,3549),(283,3598,317,3633)], "radio button", [1,2,3,4,5,6,7,8]],
                            24:["3_covid_test_type_other",(253,3651,775,4177),"text box",["without title"]],
                            25:["3_covid_specimen_type",[(805,3068,840,3102),(805,3151,840,3187),(805,3235,840,3271),(805,3320,840,3355),
                                                            (805,3404,840,3438),(805,3565,840,3600),(805,3649,840,3683),(805,3734,840,3768),(805,3970,840,4005)],"radio button",[1,2,3,4,5,6,7,8,9]],
                            26:["3_covid_specimen_type_other",(786,4019,1250,4092),"text box",["without title"]],
                            27:["3_covid_specimen_type_postmortem",(789,3866,1244,3930),"text box",["without title"]],
                            28:["3_covid_specimen_id",(1311,3040,1806,4177),"text box",["without title"]],
                            29:["3_covid_test_result",[(1843,3068,1877,3103),(1843,3152,1877,3187),(1843,3236,1877,3270),(1843,3319,1877,3355)],"radio button", [1,2,3,4]],
                            30:["3_covid_test_date_collected",(2310,3040,2644,4177),"text box",["without title"]],
                            31:["3_covid_test_date_resulted",(2650,3041,2994,4178),"text box",["without title"]],
                            32:["3_covid_lab_type",[(3013,3067,3048,3103),(3013,3228,3048,3264)],"radio button",[1,2]],
                            33:["3_covid_lab_name",(3456,3040,3994,4178),"text box",["without title"]],
                            34:["covid_lab_additional_notes",(253,4183,3993,4613),"text box",["with title","Additional test information"]]
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
        print ("page no: ", page_number)
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
df.to_csv(f'{output_folder}casereports.csv')

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

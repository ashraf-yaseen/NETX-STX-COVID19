# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 16:08:24 2020

@author: Yashar
"""


import pandas as pd
import datetime
from uszipcode import SearchEngine
import numpy as np
# =============================================================================
# This code needs uszipcode installed.
# You can install it by running:
#     pip install uszipcode
# =============================================================================

folder_path = "C:/Users/Yashar/Google Drive/UT HSC/Projects/COVID_19/Case_report_processing/"
#df = pd.read_csv(f'{folder_path}NETHealth_casereports_upto05.22.20.csv', header = 0, encoding = "ISO-8859-1", engine='python')
xl = pd.ExcelFile(f'{folder_path}NETHealth_casereports_upto05.22.20.xlsx')
df = xl.parse(xl.sheet_names[0])
df.columns = df.iloc[0]
df = df[1:]


###  creating a dictionary for zipcode in counties
county_zip_df = pd.read_csv(f'{folder_path}COUNTY_ZIP.csv', header = 0)
county_zip_dic = {}
for row in range(len(county_zip_df)):
    zipcode = int(county_zip_df.at[row,'ZIP'])
    county = county_zip_df.at[row,'County_name'][:-7]
    if county in county_zip_dic:
        county_zip_dic[county].append(zipcode)
    else:
        county_zip_dic[county] = [zipcode]
for county in county_zip_dic.keys():
    county_zip_dic[county].sort()

### processing Date
# if date is nan get the date from date of report
df['today_date'] = df.apply(lambda row: datetime.datetime.strptime(row['date_of_report'],"%m/%d/%Y")\
                            if pd.isnull(row['today_date']) else row['today_date'], axis = 1)
df['today_date'] = df['today_date'].dt.date

min_date = min(df['today_date'])
max_date = max(df['today_date'])
dates_list = pd.date_range(min_date,max_date-datetime.timedelta(days=1),freq='d').date.tolist()
dates_list.append(max_date)

### processing counties
# if county name is woods replace it with wood
df['patient_county'] = df['patient_county'].apply(lambda x: "Wood" if x == "Woods" else x)
df['patient_county'] = df['patient_county'].apply(lambda x: x if pd.isnull(x) else x.capitalize())

#if county name is missing get county name from zip code
zip_search = SearchEngine(simple_zipcode=True)
df['patient_county'] = df.apply(lambda row: zip_search.by_zipcode(str(row['patient_zip'])).county[:-7]\
                            if pd.isnull(row['patient_county']) else row['patient_county'], axis = 1)




### processing zip codes
# if zip code is missing get the zip code from city name

def find_zip_code(city, zip_code, state = "Texas"):
    if pd.isnull(zip_code) or zip_code <75000 or zip_code == 75604:
        result = zip_search.by_city_and_state(city,
                                              state,
                                              zipcode_type='Standard',
                                              sort_by='zipcode',
                                              ascending=True,
                                              returns=1)
        zipc = int(result[0].zipcode)
    else:
        zipc = zip_code
    return zipc
    
df['patient_zip'] = df.apply(lambda row: find_zip_code(str(row['patient_city']), row['patient_zip']), axis = 1)

#if county name is "Smith" double checks counties name
df['patient_county'] = df.apply(lambda row: zip_search.by_zipcode(str(row['patient_zip'])).county[:-7]\
                            if row['patient_county']=="Smith" else row['patient_county'], axis = 1)
df['patient_county'] = df['patient_county'].apply(lambda x: x if pd.isnull(x) else x.title())
counties_list = df['patient_county'].unique()

county_zipcode_dic = {}

### getting number of patients per county, zip, date
zip_count = df.groupby(['patient_county', 'patient_zip','today_date'])['patient_city'].agg('count').reset_index()
zip_count = zip_count.rename(columns={'today_date': 'date', 'patient_city': 'count_for_zip'})



for number, county in enumerate(counties_list):
    county_zip_codes = county_zip_dic[county]
    county_zipcode_dic[number] = {"county_name" : county,
                                  "county_zip_codes" : county_zip_codes}

result_column_names = ['No',
                       'patient_county',
                       'patient_zip',
                       'date']
result = pd.DataFrame(columns = result_column_names)
row = 0
dic_order = 0
for _ in county_zipcode_dic.keys():
    for zip_code in county_zipcode_dic[dic_order]['county_zip_codes']:
        for date in dates_list:
            result.at[row,'No'] = int(row+1)
            result.at[row,'patient_county'] = county_zipcode_dic[dic_order]['county_name']
            result.at[row,'patient_zip'] = int(zip_code)
            result.at[row,'date'] = date
            row +=1
    dic_order +=1


result = pd.merge(result, zip_count, on=['patient_county','patient_zip','date'], how = 'left')
county_count = result.groupby(['patient_county', 'date'])['count_for_zip'].agg('sum').reset_index()
county_count = county_count.rename(columns={'count_for_zip': 'count_for_county'})
result = pd.merge(result, county_count, on= ['patient_county','date'], how = 'left')
result.fillna(0, inplace = True)


dic_order = 0
zip_cumulative_sum = []
county_cumulative_sum = []
for _ in county_zipcode_dic.keys():
    for zip_code in county_zipcode_dic[dic_order]['county_zip_codes']:
        zip_code_cumsum = result.loc[(result['patient_county'] == county_zipcode_dic[dic_order]['county_name'])\
                                     & (result['patient_zip'] == zip_code)]
        zip_code_cumsum = list(zip_code_cumsum['count_for_zip'].cumsum(skipna = False))
        zip_cumulative_sum += zip_code_cumsum
        
        county_code_cumsum = result.loc[(result['patient_county'] == county_zipcode_dic[dic_order]['county_name'])\
                                     & (result['patient_zip'] == zip_code)]
        county_code_cumsum = list(county_code_cumsum['count_for_county'].cumsum(skipna = False))
        county_cumulative_sum += county_code_cumsum
    dic_order += 1
     
result['cumulative_count_for_zip'] = zip_cumulative_sum
result['cumulative_count_for_county'] = county_cumulative_sum

counties_data_only = result.drop_duplicates(['patient_county','date'])    
result.to_csv(f'{folder_path}Count_Summary.csv', index=False)   
counties_data_only = counties_data_only.drop(['count_for_zip',
                                              'cumulative_count_for_zip',
                                              'patient_zip'] , axis=1)     
counties_data_only.to_csv(f'{folder_path}Count_Summary_Counties_Only.csv', index=False)



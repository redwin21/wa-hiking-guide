import pandas as pd
import numpy as np
import json, re, requests, urllib
from selenium import webdriver
from bs4 import BeautifulSoup
import time

def main():
    # When running this file, a script collects all of the necessary data
    # from the WTA website.

    pass

def load_data(filepath):
    # This function loads the WTA json data, unpacks the mapped data and returns a table.
    # The feature engineering is:
    #   - elevation unpacked to gain and highest point
    #   - coordinates unpacked to lat and lon
    #   - features are one-hot-encoded
    #   - requiredPass is one-hot-encoded
    #   - length is converted to float
    # The table is returned as a pandas dataframe.
    # The table is saved as a csv.

    hikes = pd.read_json(filepath)

    hikes['highest point'] = hikes['elevation'].apply(lambda x: int(x['Highest Point'][:-4])
                                                 if not x['Highest Point'] == None else np.nan)
    hikes['gain'] = hikes['elevation'].apply(lambda x: int(x['Gain'][:-4])
                                                 if not x['Gain'] == None else np.nan)
    hikes['lat'] = hikes['coordinates'].apply(lambda x: float(x['lat'])
                                                 if not x['lat'] == None else np.nan)
    hikes['lon'] = hikes['coordinates'].apply(lambda x: float(x['lon'])
                                                 if not x['lon'] == None else np.nan)

    length_temp = hikes['length'].apply(lambda x: float(re.findall(r"(\d+\.+\d)", x)[0])
                                             if not x == None and not x == '' else np.nan)
    length_mult = hikes['length'].apply(lambda x: 2 if not x== None and 'one-way' in x else 1)

    hikes['length'] = length_temp * length_mult

    hikes['requiredPass'] = hikes['requiredPass'].apply(lambda x: 'None' if x == None else x)

    hikes = pd.get_dummies(hikes, columns=['requiredPass'], prefix='pass', prefix_sep=': ', dtype='int')

    features = pd.DataFrame()
    for f in hikes['features']:
        cols = np.array(f)
        data = np.full(cols.reshape(1,-1).shape, 1.0)
        add = pd.DataFrame(data, columns=cols)
        features = features.append(add, ignore_index=True)
    features = features.fillna(0.0)

    hikes = pd.concat([hikes, features], ignore_index=False, axis=1)

    hikes = hikes.drop(columns=['elevation','coordinates', 'features'])

    csv_path = filepath.replace('json','csv')
    hikes.to_csv(csv_path, sep='\t')

    return hikes

def add_distance(filepath):

    hikes = pd.read_csv(filepath, sep='\t', index_col=0)
    drive_time = np.full((hikes.shape[0],1), np.nan)
    drive_dist = np.full((hikes.shape[0],1), np.nan)

    for idx in range(3):
    # for idx in range(hikes.shape[0]):
        if not np.isnan(hikes['lat'][idx]):
            url = ("https://distancecalculator.globefeed.com/US_Distance_Result.asp?vr=apes&fromplace=Seattle,%20WA,%20USA&toplace="
                    + str(hikes['lat'][idx]) + "," + str(hikes['lon'][idx]) + ",US")
            # r = requests.get(url)

            driver = webdriver.Chrome(executable_path="~drivers/chromedriver.exe")
            driver.get(url)
            time.sleep(10)

            soup = BeautifulSoup(driver.page_source, 'html')
            drive_dist[idx] = soup.find('span',{'id': 'drvDistance'}).text
            drive_time[idx] = soup.find('span',{'id': 'drvDuration'}).text

    return drive_dist, drive_time


# def get_hike_pages(urls):

#     client = MongoClient('localhost', 27017)
#     db = client['wta']
#     collection = db['hike_pages']

#     for url in urls:
#         r = requests.get(url)
#         collection.insert_one({'url': url, 'route_stats_page': r.content})

# return collection

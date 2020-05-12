import pandas as pd
import numpy as np
from pymongo import MongoClient
from bson import json_util 
import json, re, requests, urllib, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def main():
    """
    When running this file, a script collects all of the necessary data from the WTA website.
    All of the necessary data files are cleaned and saved.
    """

    # hikes_path = load_data('wta-parks-data.json')
    hikes_path = 'wta-parks-data.csv'
    hikes = pd.read_csv(hikes_path, sep='\t')
    # hike_pages_path = get_hike_pages(list(hikes.index), list(hikes['url']), max_pages=0)
    # hike_pages_path = fast_get_hike_pages(list(hikes.index), list(hikes['url']))
    drive_data_path = get_drive_data(list(hikes.index), list(hikes['lat']), list(hikes['lon']))


    pass


def load_data(filepath):
    """ This function loads the WTA json data, unpacks the mapped data and returns a table.

        The feature engineering is:
        - elevation unpacked to gain and highest point
        - coordinates unpacked to lat and lon
        - features are one-hot-encoded
        - requiredPass is one-hot-encoded
        - length is converted to float

        Parameters:
            filepath: the original json file, downloaded from https://data.world/nick-hassell/washington-state-hiking-trails
        
        Returns:
            csv_path: path of dataframe saved as tab delimited csv
    """

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

    return csv_path

def get_drive_data(indices, lat, lon, wait_time=1.5):
    """ Collect drive distance and duration for each hike.

        The website https://distancecalculator.globefeed.com/ is visited for each hike. The lat and lon
        of each is fed into the url to calculate distance from Seattle to the hike.

        Parameters:
            indices: list of indices of hikes
            lat: list of latitude of hikes
            lon: list of longitude of hikes
            wait_time: time to elapse to let website calculate distances

        Returns:
            save_path: path of saved data
            saves html data to json from MongoDB
    """

    client = MongoClient('localhost', 27017)
    db = client['wta']
    collection = db['drive_data']

    for idx in indices:
        print("get_distance", idx)

        chrome_options = Options()  
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(chrome_options=chrome_options)

        if not np.isnan(lat[idx]):
            url = ("https://distancecalculator.globefeed.com/US_Distance_Result.asp?vr=apes&fromplace=Seattle,%20WA,%20USA&toplace="
                    + str(lat[idx]) + "," + str(lon[idx]) + ",US")

            driver.get(url)
            time.sleep(wait_time)
            collection.insert_one({"id": idx, 'lat': lat[idx], 'lon': lon[idx], "url": url, "content": driver.page_source})
            driver.close()

        else:
            collection.insert_one({"id": idx, 'lat': lat[idx], 'lon': lon[idx], "url": "None", "content": "None"})

    driver.quit()

    save_path = "drive-data.json"
    json.dump(json_util.dumps(collection.find()), open(save_path, "w"))

    return save_path

def clean_drive_data(filepath):
    """ This function takes the json drive data and extracts teh driving time and distance
        and returns those arrays.

        Parameters:
            filepath: file path from json data to load
        
        Returns:
            drive_dist: np array of drive distances
            drive_time: np array of drive time
    """

    data = json.load(filepath)

    drive_dist = []
    drive_time = []

    for idx in range(len(drive_dist)):

        soup = BeautifulSoup()
        drive_dist.append(soup.find('span',{'id': 'drvDistance'}).text)
        drive_time.append(soup.find('span',{'id': 'drvDuration'}).text)

        try:
            if not drive_dist[idx] == '':
                if drive_dist[idx] == 'Calculating...':
                    drive_dist[idx] = np.nan
                else:
                    drive_dist[idx] = float(drive_dist[idx].split()[0])
                
                if drive_time[idx] == 'Calculating...':
                    drive_time[idx] = np.nan
                elif len(drive_time[idx].split()) == 2:
                    drive_time[idx] = float(drive_time[idx].split()[0])
                else:
                    drive_time[idx] = float(drive_time[idx].split()[0]) * 60 + float(drive_time[idx].split()[2])
            
            else:
                drive_dist[idx] = np.nan
                drive_time[idx] = np.nan
        except:
            drive_dist[idx] = np.nan
            drive_time[idx] = np.nan

    return np.array(drive_dist), np.array(drive_time)


def get_hike_pages(indices, urls, max_pages=10):
    """ This function collects the html of each hike, as well as subsequent pages for the hike reviews.
        It does this by visiting each site, collecting the entire html, clicking the 'Next 5 Items' button
        in the reviews, and collecting that html, up to max_pages times (or when there are no more pages).

        Parameters:
            indices: list of indices of each hike
            urls: list of urls for each hike
            max_pages: int of maximum number of reviews pages to visit
        
        Returns:
            save_path: path of saved data
            saves data collection from MongoDB to json

    """

    client = MongoClient('localhost', 27017)
    db = client['wta']
    collection = db['hike_pages']

    for idx in indices:
        url = urls[idx]
        print("get_hike_pages", idx, url)
        chrome_options = Options()  
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(chrome_options=chrome_options)

        k = 0
        try:
            driver.get(url)
            collection.insert_one({"id": idx, "url": url, "page": k, "content": driver.page_source})
            time.sleep(1)

            while k < max_pages:
                k += 1
                try:
                    driver.find_element_by_partial_link_text("Next 5 items").click()
                    time.sleep(1)
                    collection.insert_one({"id": idx, "url": url, "page": k,  "content": driver.page_source})
                except:
                    break
        except:
            collection.insert_one({"id": idx, "url": url, "content": "None"})

        driver.quit()

    save_path = "wta-hike-pages.json"
    json.dump(json_util.dumps(collection.find()), open(save_path, "w"))

    return save_path

def fast_get_hike_pages(indices, urls):
    """ This function follows the procedure of the get_hike_pages function, but only visits the first page.
        Because of this, only the latest 5 reviews are scraped.
        This does not run selenium, and instead statically grabs the html, so it runs much faster.

        Parameters:
            indices: list of indices of each hike
            urls: list of urls for each hike
        
        Returns:
            save_path: path of saved data
            saves data collection from MongoDB to json

    """

    client = MongoClient('localhost', 27017)
    db = client['wta']
    collection = db['hike_pages']

    for idx in indices:
        url = urls[idx]
        print("fast_get_hike_pages", idx, url)
        r = requests.get(url)
        collection.insert_one({"id": idx, "url": url, "content": r.content})
        time.sleep(1)
    
    save_path = "wta-hike-pages.json"
    json.dump(json_util.dumps(collection.find()), open(save_path, "w"))

    return save_path


def merge_pages(hikes_path, drive_path, pages_path):

    hikes = pd.read_csv(hikes_path, sep='\t')

    # drive_dist, drive_time = clean_drive_data(drive_path)
    # hikes['drive_distance'] = drive_dist
    # hikes['drive_time'] = drive_time

    



if __name__ == '__main__':
    main()
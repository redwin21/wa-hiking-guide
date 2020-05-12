import pandas as pd
import numpy as np
from pymongo import MongoClient
from bson import json_util 
import json, re, requests, urllib, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def main():
    # When running this file, a script collects all of the necessary data
    # from the WTA website.

    hikes = load_data('wta-parks-data.json')
    get_hike_pages(list(hikes.index), list(hikes['url']))
    get_distance('wta-parks-data.csv')

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

def get_distance(filepath, wait_time=1):

    hikes = pd.read_csv(filepath, sep='\t', index_col=0)
    drive_time = []
    drive_dist = []

    for idx in range(hikes.shape[0]):
        print("get_distance", idx)

        chrome_options = Options()  
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(chrome_options=chrome_options)

        if not np.isnan(hikes['lat'][idx]):
            url = ("https://distancecalculator.globefeed.com/US_Distance_Result.asp?vr=apes&fromplace=Seattle,%20WA,%20USA&toplace="
                    + str(hikes['lat'][idx]) + "," + str(hikes['lon'][idx]) + ",US")

            driver.get(url)
            time.sleep(wait_time)
            soup = BeautifulSoup(driver.page_source, 'html')
            driver.close()

            drive_dist.append(soup.find('span',{'id': 'drvDistance'}).text)
            drive_time.append(soup.find('span',{'id': 'drvDuration'}).text)

        else:
            drive_dist.append('')
            drive_time.append('')
    
    driver.quit()

    for idx in range(len(drive_dist)):
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

    np.savetxt('drive_dist_array.txt', drive_dist)
    np.savetxt('drive_time_array.txt', drive_time)

    return np.array(drive_dist), np.array(drive_time)


def get_hike_pages(indices, urls, max_pages=10):

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

    json.dump(json_util.dumps(collection.find()), open("wta-hike-pages.json", "w"))

    return


if __name__ == '__main__':
    main()
import pandas as pd
import numpy as np
import json
import re

def main():
    # When running this file, a script collects all of the necessary data
    # from the WTA website.

    pass

def load_data(filepath):
    # This function loads the json data, unpacks the mapped data and returns a table.
    # The unpacked features are:
    #   - elevation to gain and highest point
    #   - coordinates to lat and lon
    #   - features are one-hot-encoded
    #   - requiredPass is one-hot-encoded
    # Length column is converted to float.
    # The table is returned as a pandas dataframe.
    # The table is saved as a csv.

    hikes = pd.read_json(filepath)

    hikes['highest point'] = hikes['elevation'].apply(lambda x: int(x['Highest Point'][:-4])
                                                 if not x['Highest Point'] == None else None)
    hikes['gain'] = hikes['elevation'].apply(lambda x: int(x['Gain'][:-4])
                                                 if not x['Gain'] == None else None)
    hikes['lat'] = hikes['coordinates'].apply(lambda x: float(x['lat'])
                                                 if not x['lat'] == None else None)
    hikes['lon'] = hikes['coordinates'].apply(lambda x: float(x['lon'])
                                                 if not x['lon'] == None else None)

    length_temp = hikes['length'].apply(lambda x: float(re.findall("(\d+\.+\d)", x)[0])
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
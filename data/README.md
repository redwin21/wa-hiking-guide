## Hiking Data Collection and Cleaning Process

The data for this project is collected from [Washington Trails Association](https://www.wta.org/) (WTA), a database for hikes and trip reports in Washington state.

A dataset of all of the hikes on the website, as well as urls to those hikes, can be found in a [data.world](https://data.world/nick-hassell/washington-state-hiking-trails) database. This dataset provided a prelimiary set of data, as well as an easy way to access all of the hike web pages.

All of the data is being hidden in this folder via the `.gitignore` file to avoid uploading copious amounts of unecessary data to GitHub. Anyone looking for this data can follow the same steps to collect it.

The general collection and cleaning process was performed by running the `data_collection.py` file, and is as follows:

1. The data.world data was loaded as a json and converted to a pandas dataframe. The data was converted to integers and floats as appropriate, one-hot-encoding categorical values.

2. Using the urls in the provided dataset, each web page was visited and the html was scraped. This was done using `requests` and stored in a `MongoDB` database.

3. The data in from the web pages was parsed using `BeautifulSoup`, and the additional data including the hike description was extracted and added to the main dataframe.

4. Using the acquired latitude and longitude data, a [drive distance calculator](https://distancecalculator.globefeed.com/) was visited and scraped for each hike to get the driving distance and time from Seattle to the hike trailhead. This was performed using the `selenium` library to account for calculation times on the website. This data was stored in `MongoDB`. The time and distance was extracted from the html and added to the main dataframe.

A snippet of the final dataframe information can be seen here:

```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 3412 entries, 0 to 3411
Data columns (total 37 columns):
 #   Column                                                     Non-Null Count  Dtype  
---  ------                                                     --------------  -----  
 0   name                                                       3412 non-null   object 
 1   url                                                        3412 non-null   object 
 2   length                                                     2193 non-null   float64
 3   highest point                                              1746 non-null   float64
 4   gain                                                       2043 non-null   float64
 5   lat                                                        2519 non-null   float64
 6   lon                                                        2519 non-null   float64
 7   pass: Discover Pass                                        3412 non-null   int64  
 8   pass: National Monument Fee                                3412 non-null   int64  
 9   pass: National Park Pass                                   3412 non-null   int64  
 10  pass: None                                                 3412 non-null   int64  
 11  pass: Northwest Forest Pass                                3412 non-null   int64  
 12  pass: Sno-Parks Permit                                     3412 non-null   int64  
 13  pass: Wilderness Permit                                    3412 non-null   int64  
 14  Wildflowers/Meadows                                        3412 non-null   float64
 15  Dogs allowed on leash                                      3412 non-null   float64
 16  Good for kids                                              3412 non-null   float64
 17  Lakes                                                      3412 non-null   float64
 18  Fall foliage                                               3412 non-null   float64
 19  Coast                                                      3412 non-null   float64
 20  Mountain views                                             3412 non-null   float64
 21  Wildlife                                                   3412 non-null   float64
 22  Old growth                                                 3412 non-null   float64
 23  Summits                                                    3412 non-null   float64
 24  Ridges/passes                                              3412 non-null   float64
 25  Established campsites                                      3412 non-null   float64
 26  Waterfalls                                                 3412 non-null   float64
 27  Rivers                                                     3412 non-null   float64
 28  rating                                                     3251 non-null   float64
 29  votes                                                      3251 non-null   float64
 30  reports                                                    3251 non-null   float64
 31  description                                                3251 non-null   object 
 32  drive distance                                             2031 non-null   float64
 33  drive time                                                 2031 non-null   float64
dtypes: float64(27), int64(7), object(3)
memory usage: 986.4+ KB
```

The meanings of the features are the following:

- length: hike length in miles
- highest point: max elevation of the hike in feet
- gain: elevation gain of the hike in feet
- lat: latitude of the hike
- lon: longitude of the hike
- pass: each of these features is binary (1 = True, 0 = False) whether this parking pass is required
- Dogs allowed on leash - Rivers: each of these features is binary (1 = True, 0 = False) whether this feature is present on this hike
- rating: 0-5 star rating of the hike
- votes: number of ratings for the hike
- reports: number of trip reports written for the hike
- description: text description of the hike
- drive distance: miles required to drive from Seattle to the hike
- drive time: minutes required to drive from Seattle to the hike

<img src='images/enchantments2.JPG'>

# Washington Hiking Popularity

<p align="left">
<img align="center" src="https://img.shields.io/badge/last%20modified-may%20%202020-success">
|
<img align="center" src="https://img.shields.io/badge/status-in%20progress-yellow">
</p>

<div align="left">
<a href="https://github.com/redwin21">Eddie Ressegue</a>
</div>


---

Seattlites pride themselves on their outdoor excursions. You'd be hard-pressed to find someone who didn't enjoy hiking. Washington Trails Association provides a [website](wta.org) for people to find information on hikes and discover new ones.

With the hiking community so large in the Pacific Northwest, there's a strong market for outdoor sports gear. Imagine being a gear retailer, trying to find out how to target new customers, update products and create new ones.

With hiking being so popular, there are constants efforts made to build new trails, maintain current trails, and rescue estranged hikers who lose their way. Information on why a hike is so popular can help focus resources to the best locations. It can also be used for developing new hikes in places outside of Washington.

The following models, and overall study, are meant to provide insight into what makes a hike so popular. Feature importance can be extracted from models that make predictions on popularity quanitities to make draw these insights.

---

## Table of Contents

- <a href="https://github.com/redwin21/wa-hiking-guide#data-collection-and-processing">Data Collection and Processing</a>
- <a href="https://github.com/redwin21/wa-hiking-guide#hike-description-language-processing">Hike Description Language Processing</a>  
- <a href="https://github.com/redwin21/wa-hiking-guide#ridge-regression-model">Ridge Regression Model</a> 
- <a href="https://github.com/redwin21/wa-hiking-guide#gradient-boosting-regression-model">Gradient Boosting Regression Model</a>  
- <a href="https://github.com/redwin21/wa-hiking-guide#results">Results</a>  
- <a href="https://github.com/redwin21/wa-hiking-guide#next-steps">Next Steps</a>  

---

## Data Collection and Processing

## Hiking Data Collection and Cleaning Process

The data for this project is collected from [Washington Trails Association](https://www.wta.org/) (WTA), a database for hikes and trip reports in Washington state.

A dataset of all of the hikes on the website, as well as urls to those hikes, can be found in a [data.world](https://data.world/nick-hassell/washington-state-hiking-trails) database. This dataset provided a prelimiary set of data, as well as an easy way to access all of the hike web pages.

The data was collected by visiting each of the urls in the original dataframe and scraping the html. More details can be found in the [data](https://github.com/redwin21/wa-hiking-guide/tree/master/data) folder.


<details>
<summary> Data Features </summary>
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
</details>

---

## Hike Description Language Processing

Among the data collected from WTA was the hike description, which provided a source for seeking out latent features of the data. Some natural language processing was performed to identify different features hidden in the text.

First, the text was vectorized, removing stopwords and creating term frequency matrices. Two processes approaches were taken to attempt to extract information from the text. A non-negative matrix factorization (NMF) was used to determine the most important latent features, and identify the associated words. Similarly, a K-Means clustering was done to group similar words and hikes together. Both produced similar results.

In just two clusters, and with a little bit of domain knowledge, one can clearly distinguish the difference in the two clusters:

```
['required' 'trail' 'gear' 'experience' 'park' 'peak' 'area' 'scramble' 'summit' 'expertise' 'finding' 'route' 'trails' 'mountain' 'climbing']
['trail' 'lake' 'creek' 'miles' 'mile' 'road' 'hike' 'mountain' 'forest' 'views' 'river' 'ridge' 'feet' 'way' 'trailhead']
 ```

 In this case, the first one refers to technical hiking, indicated by words like "climbing", "expertise", "gear", etc. The other cluster seems to lump together everything else.

 All number of clusters for K-Means and factors for NMF provided similar results, where one category clearly identified techncial hiking, and the others were not distinguishable. A silhouette graph of two different clusterings shows

<details>
<summary> Title </summary>

test
</details>

---

## Ridge Regression Model

<details>
<summary> Title </summary>

test
</details>

---

## Gradient Boosting Regression Model

<details>
<summary> Title </summary>

test
</details>

---

## Results

---

## Next Steps

With updates to the data and soem additional analysis, a next step for this project would be to create a hiking recommender. The recommender would act in real time to determine the best hike for a person at a certain time. It would have the following attributes:

- draw overall insights from all previous trip reports to include user sentiment about a hike and determine the best times of year
- pull the latest trip reports and perform sentiment analysis to determine if hiking conditions are currently good
- draw on the current weather forecast to determine if the weather will be appropriate at a given hike

---

<img src='images/enchantments.JPG'>
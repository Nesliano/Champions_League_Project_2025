#importing required modules
import geopy
import pandas
from geopy.exc import GeocoderTimedOut
import time
import numpy as np
import os

# Create cache to store venues in. When venues are geolocated, they will be stored here
venue_cache = {}

# Create a function that does the geocoding
def geocode(place):
    if place in venue_cache:
        return venue_cache[place]
    try:
        location = locator.geocode(place, timeout=10000, viewbox = [(67.802100, -24.809062), (22.397739, 81.837770)], bounded = True)
        if location is not None:
            venue_cache[place] = [location.latitude, location.longitude]
            return venue_cache[place]
    except GeocoderTimedOut:
        print("Not able to geocode ...", place)
    venue_cache[place] = [0, 0]  
    return venue_cache[place]



if not os.path.exists('Champions_League/Geocoded'):
    os.mkdir("Champions_League/Geocoded")

#reading CSV datasets
files = sorted(os.listdir('Champions_League/Results'))
for file in files:
    print(file)
    data = pandas.read_csv('Champions_League/Results/'+file)
    data = data.replace(np.nan, '', regex=True)
    
    # initialize geocoder
    locator = geopy.Nominatim(user_agent="john.doe@gmail.com")    
    
    
    locations = data['venue'] + ", " + data['home_nation']
    locations2 = data['home_nation']
    locations_final = data['venue']
    latitudes = []
    longitudes = []
    
    #looping to geocode addresses
    for i in range(len(locations)): 
        if 'Neutral Site' in data['venue'][i]:
            locations[i] = locations_final[i].replace('(Neutral Site)','')
        
        print("Geocoding ...", locations[i])
        l = geocode(locations[i])
        
        #Land er ikke tilgængelig for finalen, da hjemme-holdet ikke spiller hjemme.
        if l == [0,0] and 'Neutral Site' not in data['venue'][i]:
            print("Unsuccesful, changing to location 2")
            locations[i] = locations2[i]
            print("Geocoding ...", locations[i])
            l = geocode(locations[i])
            
        latitudes.append(l[0])
        longitudes.append(l[1])
        time.sleep(1)
    
    
    #save extended table to new CSV
    data['latitude'] = latitudes
    data['longitude'] = longitudes
    data['location'] = locations
    # data.to_csv(file+'-geocoded.csv', index=False, encoding='utf-8')
    data.to_csv('Champions_League/Geocoded/'+file.replace('results','geocoded'), index=False, encoding='utf-8')
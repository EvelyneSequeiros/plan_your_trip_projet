#Target : Deliver maps to give information about weather conditions in the next 7 days on key destinations in France 


# 1 - Import libraries

import requests
import pandas as pd
import plotly.io as pio
pio.renderers.default = "iframe_connected" #set up to run the script in JupiterLab
import plotly.express as px

# 2 - Create a Pandas DataFrame with all needed data to select the best destinations : geoloc & meteo 
# 2.1 - Focus on the top 35 destinations to visit in France according to OneWeekIn.com

cities = open("destinations.txt").read().splitlines()


# 2.2 Get cities geographical coordinates with an API

citylist = []
for c in cities :
        r = requests.get("https://nominatim.openstreetmap.org/search?countrycodes=fr&q="+c+"&limit=1&format=json")
        citylist.append(r.json())



# 2.3 Create 3 lists to store city IDs, latitude and longitude values

list_id = []
for i in range(len(cities)):
    list_id.append(citylist[i][0]["place_id"])
    
list_lon = []
for i in range(len(cities)):
    list_lon.append(float(citylist[i][0]["lon"]))
    
list_lat = []
for i in range(len(cities)):
    list_lat.append(float(citylist[i][0]["lat"]))



# 2.4 Get weather data for the next 7 days for each destination with an API
# using the values in the lists created previously as parameters

list_w = []
for l in range(len(list_id)):
    w = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat="+str(list_lat[l])+"&lon="+str(list_lon[l])+"&units=metric&lang=fr&exclude=current,minutely,hourly&appid=661a8bd8ce87647f3b2ff80cb303cfc6")
    list_w.append(w.json())



# 2.5 Create a dictionary to store and organize data, in order to create a DataFrame with all required information

dict_w = {}
# loop 1 : for all 35 destinations
for i in range(len(cities)):
    # store ID, latitude and longitude previously caught on lists
    weather_data = [list_id[i], cities[i], list_lon[i], list_lat[i]]
    # loop 2 : for the next 7 days (starting from "today")
    for j in range(0,7):
        # store meteo data
        daily_temp = list_w[i]["daily"][j]["temp"]["day"]
        daily_pop = list_w[i]["daily"][j]["pop"]
        daily_clouds = list_w[i]["daily"][j]["clouds"]
        if list(list_w[i]["daily"][j].keys())[17] == "rain" :
            daily_rain = list_w[i]["daily"][j]["rain"]
        else : daily_rain == 0
        daily_rain_volume_expected = daily_pop*daily_rain
        
        weather_data.extend([daily_temp,daily_pop,daily_clouds,daily_rain,daily_rain_volume_expected]) 
        
    dict_w[i+1] = weather_data


# 2.6.1 Create a DataFrame with geoloc and meteo data : first step
df = pd.DataFrame(dict_w).transpose()
df.columns = [
                "id",
                "location",
                "longitude",
                "latitude",
                "temp_j+0","pop_j+0","clouds_j+0","rain_j+0","rain_vol_j+0",
                "temp_j+1","pop_j+1","clouds_j+1","rain_j+1","rain_vol_j+1",
                "temp_j+2","pop_j+2","clouds_j+2","rain_j+2","rain_vol_j+2",
                "temp_j+3","pop_j+3","clouds_j+3","rain_j+3","rain_vol_j+3",
                "temp_j+4","pop_j+4","clouds_j+4","rain_j+4","rain_vol_j+4",
                "temp_j+5","pop_j+5","clouds_j+5","rain_j+5","rain_vol_j+5",
                "temp_j+6","pop_j+6","clouds_j+6","rain_j+6","rain_vol_j+6"
                ]

# 2.6.2 Create a DataFrame with geoloc and meteo data : aggregation for 7 days in calculated columns :
    #Calculate average cloud covering for 7 days from today
    #Calculate expected volume of rain for 7 days from today
    #Calculate average temperature for 7 days from today
df["avg_7_days_clouds"] =(df["clouds_j+0"]+df["clouds_j+1"]+df["clouds_j+2"]+df["clouds_j+3"]+df["clouds_j+4"]+df["clouds_j+5"]+df["clouds_j+6"])/7
df["7_days_expected_rain_volume"] =  df["rain_vol_j+0"]+df["rain_vol_j+1"]+df["rain_vol_j+2"]+df["rain_vol_j+3"]+df["rain_vol_j+4"]+df["rain_vol_j+5"]+df["rain_vol_j+6"]
df["avg_7_days_temp"] =(df["temp_j+0"]+df["temp_j+1"]+df["temp_j+2"]+df["temp_j+3"]+df["temp_j+4"]+df["temp_j+5"]+df["temp_j+6"])/7



# 3 : Datavizualisation with Plotly Express

# 3.1 Prerequisite : force data into numeric format

df["avg_7_days_temp"] = pd.to_numeric(df["avg_7_days_temp"])
df["7_days_expected_rain_volume"] = pd.to_numeric(df["7_days_expected_rain_volume"])
df["avg_7_days_clouds"] = pd.to_numeric(df["avg_7_days_clouds"])

#3.2 Total amount of rain (mm) to be expected within the 7 next days

fig = px.scatter_mapbox(df, 
                        lat="latitude", 
                        lon="longitude",
                        color_continuous_scale=px.colors.sequential.ice[::-1],
                        color="7_days_expected_rain_volume",
                        size="7_days_expected_rain_volume",
                        zoom=4.5, 
                        mapbox_style="carto-positron",
                        title="Total amount of rain (mm) to be expected within the 7 next days")
fig.show()

#3.3 Average cloud coverage (%) expected within the 7 next days

fig = px.scatter_mapbox(df, 
                        lat="latitude", 
                        lon="longitude",
                        color_continuous_scale=px.colors.sequential.Cividis[::-1],
                        color="avg_7_days_clouds",
                        size="avg_7_days_clouds",
                        zoom=4.5, 
                        mapbox_style="carto-positron",
                        title="Average cloud coverage (%) expected within the 7 next days")
fig.show()

#3.4 Average temperature (°C) expected within the 7 next days

3.4 fig = px.scatter_mapbox(df, 
                        lat="latitude", 
                        lon="longitude",
                        color_continuous_scale=px.colors.sequential.thermal,
                        color="avg_7_days_temp",
                        size="avg_7_days_temp",
                        zoom=4.5, 
                        mapbox_style="carto-positron",
                        title="Average temperature (°C) expected within the 7 next days")
fig.show()









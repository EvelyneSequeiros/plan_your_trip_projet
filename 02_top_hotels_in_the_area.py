
# Target : Display on the map the top 25 hotels in the area for each of the 35 destinations

# 1- Import libraries
import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
import json
import plotly.io as pio
pio.renderers.default = "iframe_connected"
import plotly.express as px

# 2-Scrap data available from the booking.com top-25-hotels result page of each of the 35 destinations with Scrapy : 
# hotel name, hotel url, description and score
# [note] : in the previous version of booking.com, geographic coordinates could be scrapped from result pages, not anymore.

# 2.1 Define spider
class BookingSpider(scrapy.Spider):

    name = "ScrapeBooking"
    start_urls = open("destinations_start_urls.txt").read().splitlines()
    def parse(self, response):
        hotellist = response.css('div._7192d3184')
        for x in hotellist:
            yield {
                'Name':x.css('h3._23bf57b84 a.fb01724e5b div.fde444d7ef._c445487e2::text').getall(),
                'Url':x.css('h3._23bf57b84 a::attr(href)').getall(),
                'Description':x.css('div._29c344764 div._4abc4c3d5::text').getall(),
                'Score':x.css('div._9c5f726ff.bd528f9ea6::text').getall()
                 }

# 2.2 launch crawler process and store the results in json file

filename = "Scrape_Booking.json"
if filename in os.listdir('src/'):
        os.remove('src/' + filename)
process = CrawlerProcess(settings = {
    'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        'src/' + filename: {"format": "json"},
    }
})
process.crawl(BookingSpider)
process.start()


# 2.3 Create left_df with scrapped data organized, to be joined later with right_df containing geographical coordinates.

booking_data = open('src/Scrape_Booking.json')
data = json.load(booking_data)

dict_data = {}
for i in range(len(data)) :
    list = []
    name = data[i]['Name'][0]
    url = data[i]['Url'][0]
    description = data[i]['Description']
    score = data[i]['Score']
    list.extend([name,url,description,score])
    dict_data[i+1] = list 

left_df = pd.DataFrame(dict_data).transpose()
df_booking.columns = [
                "name",
                "url",
                "description",
                "score"
                ]

# Add column "short_url" to simplify the url, this new column will be used to join left and right df.

left_df["short_url"]=left_df["url"].apply(lambda x : x.split("&ucfs=",1)[0])



# 3 - Scrap geographic coordinates with Scrapy (only available on each hotel's webpage)
#[NOTE] : NEED TO RESTART KERNEL TO PROCESS THE CRAWL

# 3.1 Create the list of start urls using data from the first scrapping.
hotels_url_list = [i for i in left_df["url"]]

# 3.2 Define Spider

class GeoSpider(scrapy.Spider):
    name = "geodata"
    start_urls = hotels_url_list
    handle_httpstatus_list = [500]
    
    def parse(self, response):
        geodata = response.css('div.wrap-hotelpage-top')
        return {
            
            'latlon': geodata.css('a::attr(data-atlas-latlng)').get(),
            'address': geodata.css('span.hp_address_subtitle.js-hp_address_subtitle.jq_tooltip::text').get(),
        
        # Return start url to be able to join the data with left_df
            'url': response.url,
        
        }


# 3.3 Launch crawler process and save data in a JSON file

filename = "hotelgeodata.json"
if filename in os.listdir('src/'):
        os.remove('src/' + filename)
process_geo = CrawlerProcess(settings = {
    'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        'src/' + filename : {"format": "json"},
    }
})
process_geo.crawl(GeoSpider)
process_geo.start()



# 4 - Create DataFrame df_hotels with hotel name and geographic coordinates (among others)

# 4.1 First create DataFrame right_df with new data scrapped

#Insert raw data in DataFrame right_df
geo_data = open('src/hotelgeodata.json')
hotel_geo_data = json.load(geo_data)
right_df = pd.DataFrame.from_dict(hotel_geo_data, orient='columns')

#Clean and process the data
right_df["short_url"]=right_df["url"].apply(lambda x : x.split("&ucfs=",1)[0])
right_df["latitude"]=right_df["latlon"].apply(lambda x : str(x).split(",",1)[0])
right_df["longitude"]=right_df["latlon"].apply(lambda x : str(x).split(",",1)[1])
right_df["address"]=right_df["address"].apply(lambda x : str(x).split("\n")[1])

# 4.2 Then join left_df and right_df on column "short_url"
df_hotels = pd.merge(
    left_df,
    right_df,
    how="inner",
    on="short_url",
    left_on=None,
    right_on=None,
    left_index=False,
    right_index=False,
    sort=True,
    suffixes=("_x", "_y"),
    copy=True,
    indicator=False,
    validate=None,
)


# 5 - Datavizualisation with Plotly express

# 5.1 Prerequisite
df_hotels["latitude"] = pd.to_numeric(df_hotels["latitude"])
df_hotels["longitude"] = pd.to_numeric(df_hotels["longitude"])

# 5.2 Top 25 hotels for each destination

fig = px.scatter_mapbox(df_hotels, 
                        lat="latitude", 
                        lon="longitude",
                        text="name",
                        zoom=4.5, 
                        mapbox_style="carto-positron",
                        title="Top 25 hotels for each destination")
fig.show()


# 6 - Create clean csv file

hotels=df_hotels[["name","description","score","address","latitude","longitude","short_url"]]
hotels.to_csv("20220228_hotels.csv")
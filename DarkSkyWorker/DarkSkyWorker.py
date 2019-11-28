# Imports for general configuration
import config, logging

# Imports for proper program functionality
import os, json, requests, datetime

# Global variables
TAG = 'DarkSkyWorker - '
API_KEY = config.DARK_SKY_API_KEY

# Initializing the local file environment
logging.info(TAG+'Initializing the local environment')
for path in config.LOC_FOLS.values():
    if not os.path.exists(path):
        logging.info(TAG+'Creating '+path)
        os.mkdir(path)
    else:
        logging.info(TAG+'Found '+path)

# Class to represent a viewing window
class StationWindow:
    def __init__(left_bot_cor, top_right_cor, dimensionsXY):
        return None

    def update(time):
        return None

    def step(time_delta):
        return None 

    def update_area():
        return None

    def __str__():
        return None

# Make sure to make class attributes private
class WeatherStation:
    def __init__(coordinate, time):
        self._latitude = coordinate[0]
        self._longitude = coordinate[1]
        self._sim_time = time

    # Main functionality methods
    def fill_data():
        # When filling data, use the 'del' keyword to delete
        # generated object from json once data extracted
        return None

    def generate_url():
        return None 

    # Get, set, and __str__ methods
    def get_temp():
        return None

    def get_wind_vector():
        return None

    def get_elevation():
        return None

    def get_pressure():
        return None

    def __str__():
        return None

# Add unit information, etc. in this comment
class WindVector:
    def __init__(direction, magnitude, elevation):
        self.direction = direction
        self.magnitude = magnitude
        self.elevation = elevation

    def __str__():
        return None

#Downloading some files as a test
url = 'https://api.darksky.net/forecast/'+API_KEY+'/42.3601,-71.0589,255657600?exclude=flags,hourly'
request = requests.get(url)

with open(config.LOC_FOLS['surface']+'datapoint.json', 'wb') as file:
    file.write(request.content)




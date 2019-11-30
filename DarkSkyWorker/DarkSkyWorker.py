# Imports for general configuration
import config, logging

# Imports for proper program functionality
import os, json, requests, datetime
from datetime import timezone

# Global variables
TAG = 'DarkSkyWorker - '
API_KEY = config.DARK_SKY_API_KEY

# Simple sign-extension method
def s_ext(str, length):
    while len(str) != length:
        str = '0'+str
    return str

# Class to represent a viewing window
# Create an array of weather points for the display, and then one point for the plane's 
# current location
class WeatherWindow:
    def __init__(self, left_bot_cor, right_top_cor, plane_coordinate, dimensionsXY, time):
        lat_min = left_bot_cor[0]
        lat_max = right_top_cor[0]
        lat_increment = (lat_max-lat_min) / (dimensionsXY[0] - 1)

        lon_min = left_bot_cor[1]
        lon_max = right_top_cor[1]
        lon_increment = (lon_max-lon_min) / (dimensionsXY[1] - 1)

        self._weather_grid = []
        # Outer loop
        for i in range(dimensionsXY[1]):
            weather_row = []
            lon  = lon_max - (lon_increment * i)
            # Inner loop
            for j in range(dimensionsXY[0]):
                lat = lat_min + (lat_increment * j)
                weather_row.append(WeatherPoint([lat, lon], time))
            self._weather_grid.append(weather_row)

        self._dimensions = dimensionsXY
        self._plane_datapoint = WeatherPoint(plane_coordinate, time)
        self._sim_time = time


    def update(self, time):
        return None

    def step(self, time_delta):
        return None 

    def update_area(self):
        return None

    def __str__(self):
        printout = 'WEATHER WINDOW\n*******************************************************\n'
        for i,row in enumerate(self._weather_grid):
            for j,datapoint in enumerate(row):
                printout += 'Coordinate: [' + str(j) + ', ' + str(i) + ']' + '\n'
                printout += str(datapoint) + '\n\n'
        printout += 'Dimesions of window: ' + str(self._dimensions) + '\n'
        printout += '\nPlane Datapoint:\n' + str(self._plane_datapoint) + '\n\n'
        printout += 'Simulation Time: ' + str(self._sim_time) + '\n'
        printout += '*******************************************************'
        return printout

# Class to represent the weather given a gps point and a time
class WeatherPoint:
    def __init__(self, coordinate, time):
        # Attributes specified by the user
        self.latitude = coordinate[0]
        self.longitude = coordinate[1]
        self.sim_time = time
        
        # Attributes filled from API, read only via properties
        self._wind_vector = None
        self._temperature = None
        self._humidity = None
        self._sunrise_time = None
        self._sunset_time = None
        self._precipitation_intensity = None
        self._precipitation_probability = None

        self.missing_data = False
        self.missing_wind = False

        # Filling all the data from DarkSky's API
        self.fill_data()
    
    # Setting the all attributes filled by the API as read-only
    @property
    def sim_time(self):
        return self.__sim_time

    # Converts datetime passed into sim_time into DarkSky's requested format
    @sim_time.setter
    def sim_time(self, sim_time):
        self.__sim_time  = str(sim_time.year) + '-'
        self.__sim_time += s_ext(str(sim_time.month), 2) + '-'
        self.__sim_time += s_ext(str(sim_time.day), 2) + 'T'
        self.__sim_time += s_ext(str(sim_time.hour), 2) + ':'
        self.__sim_time += s_ext(str(sim_time.minute), 2) + ':'
        self.__sim_time += s_ext(str(sim_time.second), 2)
        self.__sim_time += 'Z'                                      # This is the timezone, all times are UTC
        logging.info(TAG+'Set time: '+self.__sim_time)

    @property
    def wind_vector(self):
        return self._wind_vector

    @property
    def temperature(self):
        return self._temperature

    @property
    def humidity(self):
        return self._humidity

    @property
    def sunrise_time(self):
        return self._sunrise_time

    # Converts sunrise time given in UNIX time to datetime
    @sunrise_time.setter
    def sunrise_time(self, sunrise_time):
        self._sunrise_time = datetime.datetime.fromtimestamp(sunrise_time, timezone.utc)

    @property
    def sunset_time(self):
        return self._sunset_time

    # Converts sunset time given in UNIX time to datetime
    @sunset_time.setter
    def sunset_time(self, sunset_time):
        self._sunset_time = datetime.datetime.fromtimestamp(sunset_time, timezone.utc)

    @property
    def precipitation_intensity(self):
        return self._precipitation_intensity

    @property
    def precipitation_probability(self):
        return self._precipitation_probability

    # Fills protected attributes with data from the API
    def fill_data(self):
        # Getting and decoding the data from DarkSky API
        url = self.generate_url()
        request = requests.get(url)
        json_data = json.loads(request.content.decode('utf-8'))

        try:
            # Fills all the protected attributes of the class
            self._precipitation_intensity = json_data['currently']['precipIntensity']
            self._precipitation_probability = json_data['currently']['precipProbability']
            self._temperature = json_data['currently']['temperature']
            self._humidity = json_data['currently']['humidity']
            self.sunrise_time = json_data['daily']['data'][0]['sunriseTime']
            self.sunset_time = json_data['daily']['data'][0]['sunsetTime']
        except:
            print()
            logging.error(TAG+'ERROR: Could not get data for datapoint from DarkSky')
            self.missing_data = True
            print()
        
        try:
            direction = json_data['currently']['windBearing']
            magnitude = json_data['currently']['windSpeed']
            gusts = json_data['currently']['windGust']
            self._wind_vector = WindVector(direction, magnitude, gusts)
        except:
            print()
            logging.error(TAG+'ERROR: Could not get wind data for datapoint from DarkSky')
            self.missing_wind = True
            print()
        del json_data
        
    # Generates request URL used to get information from the API
    def generate_url(self):
        url =  'https://api.darksky.net/forecast/'
        url += API_KEY
        url += '/'+str(self.latitude)+','+str(self.longitude)
        url += ','+self.sim_time
        url += '?exclude=hourly'
        
        logging.info(TAG+'Generated url: '+url)
        return url

    def __str__(self):
        desc  = 'Latitude: ' + str(self.latitude) + '\n'
        desc += 'Longitude: ' + str(self.longitude) + '\n'
        desc += 'Time: ' + str(self.sim_time) + '\n'
        desc += '*******Wind Vector*******\n' + str(self._wind_vector) + '\n'
        desc += '*************************\n'
        desc += 'Temperature: '+ str(self._temperature) + 'F\n'
        desc += 'Humidity: ' + str(self._humidity) + '\n'
        desc += 'Sunrise Time: '+ str(self._sunrise_time) + '\n'
        desc += 'Sunset Time: '+ str(self._sunset_time) + '\n'
        desc += 'Precipitation Intensity: '+ str(self._precipitation_intensity) + '\n'
        desc += 'Precipitation Probability: '+ str(self._precipitation_probability)
        return desc

# Class to represent a wind vector, speed in mph, bearing in degrees
class WindVector:
    def __init__(self, direction, magnitude, gusts):
        self._direction = direction
        self._magnitude = magnitude
        self._gusts = gusts

    @property
    def direction(self):
        return self._direction

    @property
    def magnitude(self):
        return self._magnitude

    @property
    def gusts(self):
        return self._gusts

    def __str__(self):
        desc  = 'Wind Direction: ' + str(self._direction) + ' degrees\n'
        desc += 'Wind Speed: ' + str(self._magnitude) + ' mph\n'
        desc += 'Wind Gusts: ' + str(self._gusts)
        return desc

#Downloading some files as a test
#url = 'https://api.darksky.net/forecast/'+API_KEY+'/42.3601,-71.0589,255657600?exclude=flags,hourly'
#request = requests.get(url)

#with open(config.LOC_FOLS['data']+'datapoint.json', 'wb') as file:
#    file.write(request.content)




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

# Class to represent a viewing window in the simulation
class WeatherWindow:
    def __init__(self, left_bot_cor, right_top_cor, plane_coordinate, dimensionsXY, time):
        lat_min = left_bot_cor[0]
        lat_max = right_top_cor[0]
        lat_increment = (lat_max-lat_min) / (dimensionsXY[0] - 1)

        lon_min = left_bot_cor[1]
        lon_max = right_top_cor[1]
        lon_increment = (lon_max-lon_min) / (dimensionsXY[1] - 1)

        self._weather_grid = []
        # Code to fill self._weather_grid with current data from the darksky API
        for i in range(dimensionsXY[1]):
            weather_row = []
            lon  = lon_max - (lon_increment * i)
            for j in range(dimensionsXY[0]):
                lat = lat_min + (lat_increment * j)
                weather_row.append(WeatherPoint([lat, lon], time))
            self._weather_grid.append(weather_row)

        self._dimensions = dimensionsXY
        self._plane_datapoint = WeatherPoint(plane_coordinate, time)
        self._sim_time = time
        logging.info(TAG+'Created a new WeatherWindow Object!')

    @property
    def weather_grid(self):
        return self._weather_grid

    @property
    def plane_datapoint(self):
        return self._plane_datapoint

    # Change the time of all the data in the weather window with the argument passed
    def update_time(self, time):
        self._sim_time = time
        for row in self._weather_grid:
            for datapoint in row:
                datapoint.sim_time = self._sim_time
                datapoint.fill_data()
        self._plane_datapoint.sim_time = self._sim_time
        self._plane_datapoint.fill_data()
        logging.info(TAG+'Updated WeatherWindow time to: '+str(self._sim_time))

    # Takes a timedelta object as an argument, and increments the time of data in the window by the argument
    def step_time(self, time_delta):
        self._sim_time = self._sim_time + time_delta
        for row in self._weather_grid:
            for datapoint in row:
                datapoint.sim_time = self._sim_time
                datapoint.fill_data()
        self._plane_datapoint.sim_time = self._sim_time
        self._plane_datapoint.fill_data()
        logging.info(TAG+'Updated WeatherWindow time to: '+str(self._sim_time))

    # Updates the area of the weather window
    def update_area(self, new_left_bot, new_right_top):
        lat_min = new_left_bot[0]
        lat_max = new_right_top[0]
        lat_increment = (lat_max-lat_min) / (self._dimensions[0] - 1)

        lon_min = new_left_bot[1]
        lon_max = new_right_top[1]
        lon_increment = (lon_max-lon_min) / (self._dimensions[1] - 1)

        self._weather_grid = []
        # Code to fill self._weather_grid with current data from the darksky API
        for i in range(self._dimensions[1]):
            weather_row = []
            lon  = lon_max - (lon_increment * i)
            for j in range(self._dimensions[0]):
                lat = lat_min + (lat_increment * j)
                weather_row.append(WeatherPoint([lat, lon], self._sim_time))
            self._weather_grid.append(weather_row)
        logging.info(TAG+'Updated the weather window area')
    
    # Updates the coordinates of the aircraft
    def update_plane_data(self, new_plane_coordinates, new_time=None):
        self._plane_datapoint.latitude = new_plane_coordinates[0]
        self._plane_datapoint.longitude = new_plane_coordinates[1]

        if new_time is not None:
            self._plane_datapoint.sim_time = new_time

        self._plane_datapoint.fill_data()
        logging.info(TAG+'Updated plane coordinates to: ['+str(new_plane_coordinates[0])+', '+str(new_plane_coordinates[1])+']')

    # Updates the coordinates of the aicraft, and steps time only for the aircraft
    def step_plane_data(self, new_plane_coordinates, time_delta):
        self._plane_datapoint.sim_time = self._plane_datapoint.sim_time + time_delta
        self._plane_datapoint.latitude = new_plane_coordinates[0]
        self._plane_datapoint.longitude = new_plane_coordinates[1]

        self._plane_datapoint.fill_data()
        logging.info(TAG+'Updated plane coordinates to: ['+str(new_plane_coordinates[0])+', '+str(new_plane_coordinates[1])+']')
        logging.info(TAG+'Updated plane time to: ' + str(self._plane_datapoint.sim_time))

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
    
    @property
    def sim_time(self):
        return self.__sim_time

    @sim_time.setter
    def sim_time(self, sim_time):
        self.__sim_time = sim_time

    # Converts datetime passed into sim_time into DarkSky's requested format
    def sim_time_conversion(self):
        darksky_time  = str(self.__sim_time.year) + '-'
        darksky_time += s_ext(str(self.__sim_time.month), 2) + '-'
        darksky_time += s_ext(str(self.__sim_time.day), 2) + 'T'
        darksky_time += s_ext(str(self.__sim_time.hour), 2) + ':'
        darksky_time += s_ext(str(self.__sim_time.minute), 2) + ':'
        darksky_time += s_ext(str(self.__sim_time.second), 2)
        darksky_time += 'Z'                                      # This is the timezone, all times are UTC
        
        logging.info(TAG+'Converted datetime object to DarkSky time: '+str(self.__sim_time))
        return darksky_time

    # Setting the all attributes filled by the API as read-only
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
            self.missing_data = False
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
            self.missing_wind = False
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
        url += ','+self.sim_time_conversion()
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
        desc += 'Wind Gusts: ' + str(self._gusts) + ' mph'
        return desc

# Possible future changes:
# 1) Get rid of datapoints on the edges of _weather_grid in the WeatherWindow object, as they cannot be 
#    displayed properly, and really don't contribute too much to the aircraft analysis
#
# 2) Create a method that updates the time for a weather window, but only fills the data for
#    the plane
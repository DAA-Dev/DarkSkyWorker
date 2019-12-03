# Imports for general configuration
import config, logging

# Imports for proper program functionality
import os, json, requests, datetime
from datetime import timezone
from DarkSkyWorker import WeatherPoint, WeatherWindow

TAG = ''

# Initializing the local file environment
def init_environment():
    logging.info(TAG+'Initializing the local environment')
    for path in config.LOC_FOLS.values():
        if not os.path.exists(path):
            logging.info(TAG+'Creating '+path)
            os.mkdir(path)
        else:
            logging.info(TAG+'Found '+path)

init_environment()

window = WeatherWindow([38.149284, -108.755224], [41.951239, -102.351951], [40.0, -106.755224], [2, 3], datetime.datetime(2010, 7, 14, 9, 33, tzinfo=timezone.utc))
print(window)

#window.update_time(datetime.datetime(2016, 3, 23, 12, 34, tzinfo=timezone.utc))
#print(window)

#window.step_time(datetime.timedelta(days = 1, hours = 1))
#print(window)

#window.update_plane_coors([39.149284, -106.755224])
#print(window)

window.update_area([39.958175, -91.02172], [41.310949, -87.934570])
print(window)
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
point = WeatherPoint([38.149284, -108.755224], datetime.datetime(2010, 7, 14, 9, 33, tzinfo=timezone.utc))
print(point)

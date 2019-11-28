# Imports for general configuration
import config, logging

# Imports for proper program functionality
import os, json, requests

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

# Downloading some files as a test
url = 'https://api.darksky.net/forecast/'+API_KEY+'/42.3601,-71.0589,255657600?exclude=currently,flags'
request = requests.get(url)

with open(config.LOC_FOLS['surface']+'datapoint.json', 'wb') as file:
    file.write(request.content)




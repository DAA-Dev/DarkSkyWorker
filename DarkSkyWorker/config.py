import logging, os

# Api Keys
DARK_SKY_API_KEY = 'YOUR_KEY'
BING_MAPS_API_KEY = 'YOUR_KEY'

# All local folders needed for proper program execution
LOC_FOLS = {
    'data'    : 'data/'
}

# Configuration for program logging
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S', level=logging.NOTSET)
TAG = 'Config - '

# Method for initializing the local file environment
def init_environment():
    logging.info(TAG+'Initializing the local environment')
    for path in LOC_FOLS.values():
        if not os.path.exists(path):
            logging.info(TAG+'Creating '+path)
            os.mkdir(path)
        else:
            logging.info(TAG+'Found '+path)
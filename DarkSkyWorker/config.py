import logging

# Api Keys
DARK_SKY_API_KEY = ''
BING_MAPS_API_KEY = ''

# All local folders needed for proper program execution
LOC_FOLS = {
    'data'    : 'data/'
}

# Configuration for program logging
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S', level=logging.NOTSET)
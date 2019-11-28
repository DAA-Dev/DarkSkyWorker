import logging

# Api Keys
DARK_SKY_API_KEY = 'YOUR_KEY'

# All local folders needed for proper program execution
LOC_FOLS = {
    'data'    : 'data/',
    'surface' : 'data/surface-data'
}

# Configuration for program logging
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S', level=logging.NOTSET)
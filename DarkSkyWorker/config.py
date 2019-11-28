import logging

# Api Keys
DARK_SKY_API_KEY = 'c5eb4fdf6a8855bcfe46cc47eaaa1cda'

# All local folders needed for proper program execution
LOC_FOLS = {
    'data'    : 'data/',
    'surface' : 'data/surface-data'
}

# Configuration for program logging
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S', level=logging.NOTSET)
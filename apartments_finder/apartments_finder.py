__author__ = 'Zack Dreitzler'
__copyright__ = 'Copyright 2021, Apartments Finder'
__license__ = 'MIT'
__version__ = '0.0.1'
__status__ = 'Prototype'

from data_collection.apartmentsdotcom import get_apartmentsdotcom_data

if __name__ == '__main__':
    filters = {'bedrooms': [0, 1], 'location': 'Washington, DC'}
    get_apartmentsdotcom_data(filters=filters)

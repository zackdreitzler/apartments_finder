__author__ = 'Zack Dreitzler'
__copyright__ = 'Copyright 2021, Apartments Finder'
__license__ = 'MIT'
__version__ = '0.0.1'
__status__ = 'Prototype'

import json
import pandas as pd
import requests
from bs4 import BeautifulSoup

DEFAULT_URL = 'https://www.apartments.com/'
DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'}


def build_url(location):
    """
        Builds out the url to use in the request.
    :param location: string, the location to append to the url. I.E. 'Washington, DC'
    :return: string representing the url to use.
    """
    city = state = None
    if isinstance(location, str):
        location_parts = location.lower().split(',')
        if len(location_parts) > 1:
            city = location_parts[0].strip()
            state = location_parts[1].strip()

    if city is None or state is None:
        return DEFAULT_URL

    return DEFAULT_URL + city + '-' + state + '/'


def consume_apartments_list(apartments_dict_list, apartments_data_dict, bedroom_sizes):
    """
        Get data from apartments in apartments_dict_list
    :param apartments_dict_list: list, collection of dictionaries to consume.
    :param apartments_data_dict: dict, collection of apartments data.
    :param bedroom_sizes: list, the number of bedrooms desired.
    :return: apartments_data_dict with new apartments appended to it.
    """

    for apartment in apartments_dict_list:
        name = apartment['name']
        address = f"{apartment['Address']['streetAddress']}, " \
                  f"{apartment['Address']['addressLocality']}, " \
                  f"{apartment['Address']['addressRegion']} {apartment['Address']['postalCode']}"

        url_with_additional_info = apartment['url']
        apartment_page = request_page(url_with_additional_info, DEFAULT_HEADERS)

        # Get policies of this property
        string_of_all_policies = get_policies(apartment_page)

        # Get website URL
        website = get_website(apartment_page)

        # Get each floorplan and append to the data dictionary
        filtered_beds = ['bed'+str(bedroom) for bedroom in bedroom_sizes]

        floorplan_buckets = apartment_page.find_all(lambda tag: tag.name == 'div'
                                                         and tag.get('data-tab-content-id') in filtered_beds)

        for floorplan_bucket in floorplan_buckets:
            floorplans = floorplan_bucket.find_all(lambda tag: tag.name == 'div'
                                                             and tag.get('class') == ['priceBedRangeInfo'])
            for floorplan in floorplans:

                price, bed, bath, size = get_floorplan_details(floorplan)

                apartments_data_dict['name'].append(name)
                apartments_data_dict['price'].append(price)
                apartments_data_dict['size'].append(size)
                apartments_data_dict['bedrooms'].append(bed)
                apartments_data_dict['bathrooms'].append(bath)
                apartments_data_dict['address'].append(address)
                apartments_data_dict['policies'].append(string_of_all_policies)
                apartments_data_dict['website'].append(website)

    return apartments_data_dict



def get_apartments_list(page_souped):
    """
        Takes a page that has been passed through BeautifulSoup and gets the list of results on the page.
    :param page_souped: <class 'bs4.BeautifulSoup'>, a page that has been passed through BeautifulSoup().
    :return: list of dictionaries from the given page.
    """

    scripts_parsed = page_souped.find_all(lambda tag: tag.name == 'script' and tag.get('type') == 'application/ld+json')
    apartments_list = json.loads(scripts_parsed[0].contents[0])['about']
    return apartments_list


def get_floorplan_details(floorplan):
    """
        Get the details about the given floorplan. Such as number of bedrooms and bathrooms.
    :param floorplan: <class 'bs4.BeautifulSoup'>, a page that has been passed through BeautifulSoup().
    :return: the price, number of bedrooms, number of bathrooms, and square footage of the apartment
    """
    # Get Price
    price = floorplan.find_all(lambda tag: tag.name == 'span'
                                           and tag.get('class') == ['rentLabel'])[0].contents[0].strip()

    # Get size, bedroom number, and bathrooms number
    bed = None
    bath = None
    size = None
    floorplan_details = floorplan.find_all(lambda tag: tag.name == 'span'
                                                       and tag.get('class') == ['detailsTextWrapper'])[0].contents
    for floorplan_detail in floorplan_details:
        try:
            floorplan_detail_str = floorplan_detail.contents[0].lower()
            if 'bed' in floorplan_detail_str:
                bed = floorplan_detail_str
            elif 'studio' in floorplan_detail_str:
                bed = 'Studio'
            if 'bath' in floorplan_detail_str:
                bath = floorplan_detail_str
            elif 'sq ft' in floorplan_detail_str:
                size = floorplan_detail_str
        except AttributeError:
            # The item was not of type Tag
            pass
        except IndexError:
            print(f'This floorplan has no details')
            pass
    return price, bed, bath, size


def get_num_pages(page_souped):
    """
        This gets the number of pages to search through.
    :param page_souped: <class 'bs4.BeautifulSoup'>, a page that has been passed through BeautifulSoup().
    :return: int, the number of pages to search through
    """

    span_parsed = page_souped.find_all(lambda tag: tag.name == 'span' and tag.get('class') == ['pageRange'])
    span_parsed_contents_list = span_parsed[0].contents[0].split(' ')
    return int(span_parsed_contents_list[-1])



def get_policies(apartment_page):
    """
        Appends all policy groups together to form one policy string.
    :param apartment_page: <class 'bs4.BeautifulSoup'>, a page that has been passed through BeautifulSoup().
    :return: string containing all apartment policies.
    """
    policies = apartment_page.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['feespolicies'])
    string_of_all_policies = ''
    for policy in policies:
        policy_header = policy.find('h4').contents[0].upper()
        policy_details = policy.find_all(lambda tag: tag.name == 'div'
                                                     and tag.get('class') in [['column'], ['column-right']])
        policy_list = [detail for detail_list in [detail.contents for detail in policy_details] for detail in
                       detail_list]

        policy_list_combined = policy_list
        if len(policy_list) >= 2:
            policy_list_combined = [f"{head}: {fee}" for head, fee in zip(policy_list[::2], policy_list[1::2])]
        policy_str = f"{policy_header} " + ', '.join(policy_list_combined)
        string_of_all_policies += f'    {policy_str}'
    return string_of_all_policies


def get_website(apartment_page):
    """
        Get the website URL for the apartment
    :param apartment_page: <class 'bs4.BeautifulSoup'>, a page that has been passed through BeautifulSoup().
    :return: a string of the website URL of the apartment.
    """
    website_tag = apartment_page.find_all((lambda tag: tag.name == 'a' and tag.get('title') == 'View Property Website'))
    try:
        website = website_tag[0].get('href')
        return website
    except IndexError:
        print('A URL does not exist for apartment')
    return None


def request_page(url, headers, timeout=5):
    """
        Make a GET request to the given url with the given headers and return the contents passed through BeautifulSoup.
    :param url: string, the url to use in the request.
    :param headers: dict, the headers to append to the HTTP request.
    :param timeout: int, the amount of seconds to wait before timing out the request.
    :return: the requested page passed through BeautifulSoup.
    """
    try:
        page = requests.get(url, headers=headers, timeout=timeout)
        page_souped = BeautifulSoup(page.content, 'html.parser')
    except requests.exceptions.MissingSchema:
        print(f'URL: "{url}" not valid.')
        return None
    except requests.exceptions.ConnectionError:
        print(f'Failed to connect to URL: "{url}".')
        return None

    return page_souped


def get_apartmentsdotcom_data(filters=None, headers=DEFAULT_HEADERS):
    """
        Gets apartments data from apartments.com.
    :param filters: the filters to apply to the request.
    :param headers: the HTTP headers for the request.
    :return: dictionary containing lists with the following keys;
       'name', 'price', 'size', 'bedrooms', 'bathrooms', 'address', 'policies', website'
    """

    url = build_url(filters.get('location'))
    bedrooms = filters.get('bedrooms')

    apartments_data_dict = {
        'name': []
        , 'price': []
        , 'size': []
        , 'bedrooms': []
        , 'bathrooms': []
        , 'address': []
        , 'policies': []
        , 'website': []
    }

    page_contents = request_page(url, headers)
    if page_contents:
        num_pages = get_num_pages(page_contents)
        apartments_dict_list = get_apartments_list(page_contents)
        apartments_data_dict = consume_apartments_list(apartments_dict_list, apartments_data_dict, bedrooms)

        for num in range(2, num_pages+1):
            page_contents = request_page(url+f'{num}', headers)
            apartments_dict_list = get_apartments_list(page_contents)
            apartments_data_dict = consume_apartments_list(apartments_dict_list, apartments_data_dict, bedrooms)

    apartments_as_dataframe = pd.DataFrame(apartments_data_dict)

    return apartments_as_dataframe

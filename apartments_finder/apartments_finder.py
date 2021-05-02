__author__ = 'Zack Dreitzler'
__copyright__ = 'Copyright 2021, Apartments Finder'
__license__ = 'MIT'
__version__ = '0.0.1'
__status__ = 'Prototype'

import json
import requests

from bs4 import BeautifulSoup


def get_num_pages(page_souped):
    """This gets the number of pages to search through.

    :param page_souped: <class 'bs4.BeautifulSoup'>, a page that has been passed through BeautifulSoup().
    :return: int, the number of pages to search through
    """
    span_parsed = page_souped.find_all(lambda tag: tag.name == 'span' and tag.get('class') == ['pageRange'])
    span_parsed_contents_list = span_parsed[0].contents[0].split(' ')
    return int(span_parsed_contents_list[-1])


def get_apartments_list(page_souped, current_list):
    """Takes a page that has been passed through BeautifulSoup and gets the list of results on the page.

    :param page_souped: <class 'bs4.BeautifulSoup'>, a page that has been passed through BeautifulSoup().
    :param current_list: list, the current list of apartments.
    :return: list of dictionaries from the given page.
    """
    scripts_parsed = page_souped.find_all(lambda tag: tag.name == 'script' and tag.get('type') == 'application/ld+json')
    apartments_list = json.loads(scripts_parsed[0].contents[0])['about']
    return current_list + apartments_list


def request_page(url, headers, timeout=5):
    """Make a GET request to the given url with the given headers and return the contents passed through BeautifulSoup.

    :param url: string, the url to use in the request.
    :param headers: dict, the headers to append to the HTTP request.
    :param timeout: int, the amount of seconds to wait before timing out the request.
    :return: the requested page passed through BeautifulSoup.
    """
    page = requests.get(url, headers=headers, timeout=5)
    page_souped = BeautifulSoup(page.content, 'html.parser')
    return page_souped


if __name__ == '__main__':
    default_url = 'https://www.apartments.com/philadelphia-pa/'
    default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'}
    page_contents = request_page(default_url, default_headers)

    num_pages = get_num_pages(page_contents)
    apartments_dict_list = get_apartments_list(page_contents, [])
    print(apartments_dict_list[0])
    # for num in range(2, num_pages+1):
    #     page_contents = request_page(default_url+f'{num}/', default_headers)
    #     apartments_dict_list = get_apartments_list(page_contents, apartments_dict_list)

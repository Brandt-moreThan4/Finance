from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
import string
from pathlib import Path
import pandas as pd
import os

cd = Path(os.path.curdir)


def get_soup(url: str):
    """Returns beautiful Soup object of the requested page or None if there was trouble somewhere along the way."""

    page_response = get_page_response(url)
    if page_response is not None:
        try:
            soup = BeautifulSoup(page_response.text)
        except:
            print('Trouble parsing the soup for: {}'.format(url))
            return None
        else:
            return soup
    else:
        print('The response object was "None" so there is no point in trying to parse')
        return None


def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
    Uses a whitelist approach: any characters not present in valid_chars are
    removed. Also spaces are replaced with underscores.
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    return filename


def get_page_response(url):
    """Get a page response using the given url"""
    try:
        page_response = requests.get(url)
    except:
        print('Error loading url')
        return None
    else:
        return page_response


def get_chrome_driver():
    """Returns a selenium driver object to manipulate chrome"""

    driver_path = Path(r'C:\Users\15314\OneDrive\Desktop') / 'chromedriver.exe'
    options = webdriver.chrome.options.Options()
    options.set_headless(headless=True)
    # try:
    driver = webdriver.Chrome(driver_path, options=options)
    # except:
    #     print('Something screwed up getting the driver. Make sure chrome is downloaded and the path is correct')
    # return None
    # else:
    return driver


def time_usage(func):
    def wrapper(*args, **kwargs):
        begin_time = time.time()
        retval = func(*args, **kwargs)
        end_time = time.time()
        print(f"elapsed time: {(end_time - begin_time)}")
        return retval

    return wrapper


def load_ciks(source: str = 'file'):
    """Returns a pandas dataframe. Contains 3 columns: cik; ticker; name"""
    if source == 'file':
        df = pd.read_csv(cd / 'ciks.csv', index_col='index', dtype={'cik': str})
    elif source == 'sec':
        url = 'https://www.sec.gov/files/company_tickers.json'
        df = pd.read_json(url).T
        df.rename(columns={'cik_str': 'cik', 'title': 'name'})
    else:
        Exception('Sorry, that is not a valid data source input')
    return df


def make_url(base_url, components):
    """Eases the creation of urls"""
    url = base_url

    # add each base component to the base url
    for component in components:
        url += f'/{component}'
        # url = f'{url}/{component}'
    return url

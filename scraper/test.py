# https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000092380&type=10-k&dateb=&owner=exclude&count=40&search_text=

"""This is going to be a program to try to scrape info from 10-k's"""

import requests
import time
import os
from pathlib import Path

import scraper.scrapefunctions as sp

cd = Path(os.path.curdir)
# dicky = sp.load_ciks()

# base_url = r'https://www.sec.gov/Archives/edgar/data'
#
# cik_num = '/886982/'
# filings_url = base_url + cik_num + 'index.json'
#
# content = requests.get(filings_url)
# decoded_content = content.json()
#
# filing_number = decoded_content['directory']['item'][0]['name']
# filing_url = base_url + cik_num + filing_number + '/index.json'
#
# new_content = requests.get(filing_url)
# document_content = new_content.json()
#
#
# for document in document_content['directory']['item']:
#
#     if document['type'] != 'image2.gif':
#         doc_name = document['name']
#         document_url = base_url + cik_num + filing_number + '/' + doc_name
#         print(document_url)
#
#
# dicky.to_csv(cd / 'ciks.csv', index_label=)
print('lol')

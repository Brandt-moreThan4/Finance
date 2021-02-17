import requests
import pandas as pd
from bs4 import BeautifulSoup

# https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000092380&type=10-k&dateb=&owner=exclude&count=40&search_text=

"""This is going to be a program to try to scrape info from 10-k's"""

import requests
import time
import os
from pathlib import Path

import scraper.scrapefunctions as sp

cd = Path(os.path.curdir)
# convert a normal url to a document url
normal_url = r"https://www.sec.gov/Archives/edgar/data/1265107/0001265107-19-000004.txt"
normal_url = normal_url.replace('-', '').replace('.txt', '/index.json')

# Base url for the daily index files
BASE_URL = r'https://www.sec.gov/'

DOCUMENTS_URL = r'https://www.sec.gov/Archives/edgar/data/1265107/000126510719000004/index.json'

# request the url and decode it.
content = requests.get(DOCUMENTS_URL)
content = content.json()

for file in content['directory']['item']:
    if file['name'] == 'FilingSummary.xml':
        xml_summary = BASE_URL + content['directory']['name'] + '/' + file['name']
        print(xml_summary)

BASE_URL = xml_summary.replace('FilingSummary.xml', '')

content = requests.get(xml_summary).content
soup = BeautifulSoup(content, 'lxml')
reports = soup.find('myreports')

master_reports = []
for report in reports.find_all('report')[:-1]:
    report_dict = {'name_short': report.shortname.text, 'name_long': report.longname.text,
                   'position': report.position.text,
                   'category': report.menucategory.text, 'url': BASE_URL + report.htmlfilename.text}

    master_reports.append(report_dict)
    print('-' * 100)
    print(report_dict)

statements_url = []
for report_dict in master_reports:
    # define the statements we want to look for.
    item1 = r"Consolidated Balance Sheets"
    item2 = r"Consolidated Statements of Operations and Comprehensive Income (Loss)"
    item3 = r"Consolidated Statements of Cash Flows"
    item4 = r"Consolidated Statements of Stockholder's (Deficit) Equity"

    # store them in a list.
    report_list = [item1, item2, item3, item4]

    if report_dict['name_short'] in report_list:
        statements_url.append(report_dict['url'])

statements_data = []

for statement in statements_url:
    statement_data = {}
    statement_data['headers'] = []
    statement_data['sections'] = []
    statement_data['data'] = []

    content = requests.get(statement).content
    report_soup = BeautifulSoup(content, 'html')

    # include th too?
    for index, row in enumerate(report_soup.table.find_all('tr')):
        cols = row.find_all('td')

        if len(row.find_all('th')) == 0 and len(row.find_all('strong')) == 0:
            reg_row = [element.text.strip() for element in cols]
            statement_data['data'].append(reg_row)
        elif len(row.find_all('th')) == 0 and len(row.find_all('strong')) != 0:
            section_row = cols[0].text.strip()
            statement_data['sections'].append(section_row)
        elif len(row.find_all('th')) != 0:
            header_row = [element.text.strip() for element in row.find_all('th')]
            statement_data['headers'].append(header_row)
        else:
            print('Error')

    statements_data.append(statement_data)

income_headers = statements_data[1]['headers'][1]
income_data = statements_data[1]['data']

income_df = pd.DataFrame(income_data)
income_df.index = income_df[0]
income_df.index.name = 'Category'
income_df = income_df.drop(0,axis=1)

income_df = income_df.replace('[\$,)]', '', regex=True).replace('[(]','-', regex=True).replace('', 'Nan', regex=True)

income_df = income_df.astype(float)
income_df.columns = income_headers

print(income_df)

print('lol')

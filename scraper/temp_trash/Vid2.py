# https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000092380&type=10-k&dateb=&owner=exclude&count=40&search_text=

"""This is going to be a program to try to scrape info from 10-k's"""

import requests
import time
import os
from pathlib import Path

import scraper.scrapefunctions as sp

cd = Path(os.path.curdir)

# Base url for the daily index files
# BASE_URL = r'https://www.sec.gov/Archives/edgar/daily-index'
#
# # daily index for url for 2019
# year_url = sp.make_url(BASE_URL, ['2019', 'index.json'])
# content = requests.get(year_url).json()
#
# for quarter in content['directory']['item']:
#
#     # get the name of the folder
#     quarter_name = quarter['name']
#     print(f'Getting the url for quarter: {quarter_name}')
#     quarter_url = sp.make_url(BASE_URL,['2019', quarter_name, 'index.json'])
#
#     file_content = requests.get(quarter_url).json()
#     print('About to get wil pulling a bunch of files')
#
#     for file in file_content['directory']['item']:
#         file_url = sp.make_url(BASE_URL, ['2019', quarter_name, file['name']])
#         print(file_url)


file_url = r'https://www.sec.gov/Archives/edgar/daily-index/2019/QTR4/master.20191001.idx'

# Download content and write it to text file
content = requests.get(file_url).content

# with open('master1.txt', 'wb') as f:
#     f.write(content)

with open('master1.txt', 'rb') as f:
    byte_date = f.read()

# Finding the starting index
data = byte_date.decode('utf-8').split('  ')
start_ind = 0
for index, item in enumerate(data):
    if 'ftp://ftp.sec.gov/edgar/' in item:
        start_ind = index
        break

# Remove the junk
data_format = data[start_ind + 1:]

master_data = []

for index, item in enumerate(data_format):
    if index == 0:
        cleaned_item_data = item.replace('\n', '|').split('|')
        # What is the below?
        cleaned_item_data = cleaned_item_data[8:]
    else:
        cleaned_item_data = item.replace('\n', '|').split('|')

    for pointer, row in enumerate(cleaned_item_data):

        # find the text file
        if '.txt' in row:
            # misses the first one I think.
            mini_list = cleaned_item_data[(pointer - 4): (pointer + 1)]
            if mini_list:
                mini_list[4] = "https://www.sec.gov/Archives/" + mini_list[4]
                master_data.append(mini_list)

            # print(mini_list)

# Make this better
for index, document in enumerate(master_data):
    # Make it a dictionary
    document_dict = {'cik_number': document[0], 'company_name': document[1], 'form_id': document[2],
                     'date': document[3], 'file_url': document[4]}

    master_data[index] = document_dict

for document_dic in master_data:
    # print(document_dic)
    # Below picks up stuff that is not just a 10-k
    if '10-K' in document_dic['form_id']:
        print(f'10-K for: {document_dic["company_name"]}\n {document_dic["file_url"]}')

# print(data_format)
print('lol')

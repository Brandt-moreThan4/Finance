import requests
from bs4 import BeautifulSoup
import time
from dateutil.parser import parse
from pathlib import Path
import os

import scraper.scrapefunctions as sp

SEARCH_ROOT = r'https://www.sec.gov/cgi-bin/browse-edgar?'
SEC_DATA_ROOT = 'https://www.sec.gov/'
cik_df = sp.load_ciks()
# TICKERS = ['SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
TICKERS = ['SBUX']


class SearchUrl:
    """date_before should be in format of 'YYYYMMDD'
     If you don't want the output to come as the rss feed then just put output to an empty string
     """

    def __init__(self, cik, action='getcompany', doc_type='', date_before='', count=10, output='atom'):
        self.cik = cik
        self.action = action
        self.doc_type = doc_type
        self.date_before = date_before
        self.count = count
        self.output = output

    def as_search_string(self):
        """Return the correctly formatted query string to plug at the end of the url"""
        # Maybe just drop the if conditions and include blank query values since it is the same as not putting it?

        query_string = f'action={self.action}&CIK={self.cik}'
        if self.doc_type:
            query_string += f'&type={self.doc_type}'
        if self.date_before:
            query_string += f'&dateb={self.date_before}'
        query_string += f'&count={self.count}'
        if self.output:
            query_string += f'&output={self.output}'

        return query_string


class TenK:

    def __init__(self):
        self.accession_number = None
        self.index_link = None
        self.report_link = None
        self.report_date = None
        self.ticker = None

    def __repr__(self):
        if self.report_date is not None:
            return str(self.report_date)


all_10ks = []
for ticker in TICKERS:
    cik_num = cik_df[cik_df.ticker == ticker].cik.iloc[0]
    url = SEARCH_ROOT + SearchUrl(cik=cik_num, doc_type='10-k', count=10).as_search_string()
    search_result = requests.get(url).content
    search_soup = BeautifulSoup(search_result, parser='xml')

    # Pull out the relevant info from the xml file
    # For now, the only relevant info is the accession_number (actually prolly not needed) and the link the 10-k's index

    for entry in search_soup.find_all('entry'):
        ten_k = TenK()
        ten_k.ticker = ticker
        ten_k.accession_number = entry.find('accession-number').get_text()
        ten_k.index_link = entry.find('filing-href').get_text()
        all_10ks.append(ten_k)

    for ten_k in all_10ks:
        # Navigate to index page and scoop up the link to the 10-k report
        index_soup = sp.get_soup(ten_k.index_link)
        if index_soup is not None:
            # Below assuming it will always be the first table. Safe assumption? Probably not. Could use {'class':
            # 'tableFile'}
            report_table = index_soup.find('table')
            for row in report_table.find_all('tr'):
                cols = row.find_all(['th', 'td'])
                # The url is in the 3rd cell and the doc type is in the 4th
                document_type = cols[3].get_text().lower()
                # Below ignores report amendments
                if document_type == '10-k':
                    document_link = cols[2].find('a')
                    if document_link is not None:
                        # Get rid of the ix part which would take you to the interactive document
                        document_link = document_link.get('href')
                        document_link = document_link.replace('/ix?doc=/', '')
                        ten_k.report_link = SEC_DATA_ROOT + document_link
                    break

            # Get the date of the report and convert it to datetime.date
            try:
                period_text = index_soup.find(string='Period of Report')
                report_date = period_text.parent.find_next_sibling().get_text()
                ten_k.report_date = parse(report_date).date()
            except:
                print(f'Sorry, could not get the date for {ten_k.index_link}')

        # Small sleep between each url request so that I am not being a dick to edgar's server.
        time.sleep(.1)

# Save the html of each 10k report in folder
for ten_k in all_10ks:
    time.sleep(.1)  # Don't be a dick!
    if ten_k.report_link is not None:
        response = requests.get(ten_k.report_link)
        report_soup = BeautifulSoup(response.content, 'lxml')
        file_path = Path().cwd() / '10ks' / ten_k.ticker / (str(ten_k.report_date) + '.html')
        if not file_path.parent.exists():
            file_path.parent.mkdir()
        html = str(report_soup)
        try:
            with file_path.open(mode='w') as f:
                f.write(html)
        except Exception as e:
            try:
                html = sp.restore_windows_1252_characters(html)
                with file_path.open(mode='w') as f:
                    f.write(html)
            except Exception as e:
                # Below encoding kind of causes some weirdness in certain reports I think
                print(f'sorry could not do the good format for {ten_k.report_date}\nerror:{e}')
                with file_path.open(mode='w', encoding='utf-8') as f:
                    f.write(html)

    else:
        print(f'Uh oh. There was no page response for this url: {ten_k.report_date}')

print('lol')

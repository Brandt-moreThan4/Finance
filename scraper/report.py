"""Put something here.
Things to do:
1. Figure out why the encoding gets all weird when I try to save the html to a file on my computer
2. refactor everything to make it all better.
3. update the below to make it more generic. Incorporate not just 10-ks.
4. Prolly a bunch of other stuff.
"""

from bs4 import BeautifulSoup
from bs4.element import Tag
import time
from dateutil.parser import parse
from pathlib import Path
import unicodedata
import re
import pandas as pd

import scraper.scrapefunctions as sp

SEARCH_ROOT = r'https://www.sec.gov/cgi-bin/browse-edgar?'  # Used to build the search url
SEC_DATA_ROOT = 'https://www.sec.gov/'  # Used to build the 10k report url
cik_df = sp.load_ciks()


def build_search_url(cik, action='getcompany', doc_type='', date_before='', count=10, output='atom'):
    """date_before should be in format of 'YYYYMMDD'
     If you don't want the output to come as the rss feed then just put output to an empty string
     Account minimum on the feed is 10
     """
    query_string = f'{SEARCH_ROOT}action={action}&CIK={cik}&type={doc_type}&dateb={date_before}&count={count}&output={output}'
    return query_string


def get_cik(ticker: str):
    """Returns the cik, or raises an exception if there is no ticker."""
    return cik_df[cik_df.ticker == ticker].cik.iloc[0]


class Report:
    """This class is used to hold info for a specific report. Right now it is sort of just build for 10-k"""

    def __init__(self, ticker, report_type, accession_number=None, index_link=None, report_link=None, report_date=None,
                 cik=None):

        self.accession_number = accession_number
        self.index_link = index_link
        self.report_link = report_link
        self.report_date = report_date
        self.ticker = ticker
        self.report_type = report_type

    @property
    def cik(self):
        """Returns the cik, or raises an exception if there is no ticker."""
        if self.ticker:
            return cik_df[cik_df.ticker == self.ticker].cik.iloc[0]
        else:
            Exception(f'Sorry, this report must have a ticker to look up the cik number.')

    def scrape_index_page(self):
        """Extract info from the report index page. Includes: date of report and the report link."""
        if self.index_link:
            index_soup = sp.get_soup(self.index_link)
            if index_soup:
                # Below assuming it will always be the first table. Safe assumption? Probably not. Could use {'class':
                # 'tableFile'}
                report_table = index_soup.find('table')
                for row in report_table.find_all('tr'):
                    cols = row.find_all(['th', 'td'])
                    # The url is in the 3rd cell and the doc type is in the 4th
                    document_type = cols[3].get_text().lower()
                    # Below ignores report amendments
                    if document_type == self.report_type.lower():
                        document_link = cols[2].find('a')
                        if document_link:
                            # Get rid of the ix part which would take you to the interactive document
                            document_link = document_link.get('href')
                            document_link = document_link.replace('/ix?doc=/', '')
                            self.report_link = SEC_DATA_ROOT + document_link
                        break

                # Get the date of the report and convert it to datetime.date
                try:
                    report_date = index_soup.find(string='Period of Report').parent.find_next_sibling().get_text()
                    self.report_date = parse(report_date).date()
                except:
                    print(f'Sorry, could not get the date for {self.index_link}')

    def get_report_soup(self):
        """Returns beautiful soup object of the report"""
        report_soup = sp.get_soup(self.report_link)
        return report_soup

    def __repr__(self):
        # if self.report_date is not None:
        return f'{self.ticker}: {str(self.report_date)}'


def save_reports(report_dict: dict):
    """Save each of the reports in current directory under 10k folder. Each dict value should contain a list of Reports
     Many of the reports turn out weird because of encoding errors. Need to learn what's going on and fix it.
    """

    for report_list in report_dict.values():
        for ten_k in report_list:
            time.sleep(.1)  # Don't be a dick!
            if ten_k.report_link:
                report_soup = ten_k.get_report_soup()
                file_path = Path().cwd() / '10ks' / ten_k.ticker / (str(ten_k.report_date) + '.html')
                if not file_path.parent.exists():
                    file_path.parent.mkdir()
                html = str(report_soup)
                try:
                    with file_path.open(mode='w') as f:
                        f.write(html)
                except Exception as e:
                    # Below encoding kind of causes some weirdness in certain reports.
                    print(f'sorry could not do the good format for {ten_k.ticker}: {ten_k.report_date}\nerror:{e}')
                    with file_path.open(mode='w', encoding='utf-8') as f:
                        f.write(html)

            else:
                print(f'Uh oh. There was no page response for this url: {ten_k.report_date}')


def scoop_reports(tickers, report_count=5) -> dict:
    """Pass in tickers and spit out a dictionary containing reports with tickers as the dictionary key."""
    # May have to look at the html on edgar's website to really understand some of this.

    all_reports = {}
    for ticker in tickers:
        url = SEARCH_ROOT + build_search_url(cik=get_cik(ticker), doc_type='10-k', count=report_count)
        search_soup = sp.get_soup(url)
        report_soups = search_soup.find_all('entry')  # There is an entry tag associated with each report
        report_count = min(report_count, len(report_soups))

        all_reports[ticker] = []
        for entry in report_soups[0:report_count]:
            # Pull out the index link from the xml file
            ten_k = Report(ticker=ticker, report_type='10-k', index_link=entry.find('filing-href').get_text())
            # Get report link and date off of index page
            ten_k.scrape_index_page()
            all_reports[ticker].append(ten_k)
            time.sleep(.1)  # Small sleep between each url request so that I am not being a dick to edgar's server.

    return all_reports


def get_balance_sheet_table(report_soup: BeautifulSoup) -> Tag:
    """Returns table that contains the balance sheet"""
    return report_soup.find(locate_balance_sheet_table)


def locate_balance_sheet_table(tag: Tag, match_threshold: float = .5) -> bool:
    """Should locate the balance sheet header. Does so by looking for a certain amount of keywords in the table and
        checking to see if the percentage of keywords is greater than the threshold.
    """
    # Should update this so that the user can input their own list of keywords?
    # Perhaps make this a nested function inside of a more general one to locate any financial statement?
    # Each statement having its own sub function and default keywords?

    # Basically this looks at each table and returns a match if the table contains enough of the keywords.
    if tag.name == 'table':
        bs_keywords = ['assets', 'currents assets', "STOCKHOLDERS' EQUITY", 'Retained earnings', 'Current liabilities',
                       'Accounts payable']
        bs_keywords = [keyword.lower() for keyword in bs_keywords]
        tag_text = tag.get_text().lower()
        matches = [keyword in tag_text for keyword in bs_keywords]
        return sum(matches) / len(bs_keywords) >= match_threshold
    else:
        return False


def clean_row(row_soup: Tag) -> list:
    """Send in a list and return a cleaner list. This method is sketchy though and will need refining and testing"""
    # The goal is to make sure each row only has three columns. The loop should delete any cell that is not an account
    # description or number or hyphen ( which indicates 0 usually)

    # Converts some weird blank strings into normal blank python strings
    cols = row_soup.find_all('td')
    row = [unicodedata.normalize("NFKD", col.get_text()) for col in cols]

    # Don't get stuck in an infinite loop. Just in case my cleaning doesn't trim everything down enough
    loop_count = 0
    while len(row) > 3 and loop_count < 40:
        loop_count += 1
        for col_index, col in enumerate(row):
            if not re.search('[\w-]', col):  # Don't delete a letter, number or hyphen
                if col_index != 0:  # Don't delete the cell in the first column. This isn't the best logic
                    row.pop(col_index)
                    break
    return row


def clean_and_extract_bs(report_soup: BeautifulSoup) -> pd.DataFrame:
    """Input a beautiful soup table tag and then returns a pandas data frame of the cleaned balance sheet."""

    # Just pull out each cell in the table and try to eliminate any that are just placeholders so you can extract a
    # table with equal columns that makes sense.

    bs_table = get_balance_sheet_table(report_soup)
    table_rows = bs_table.find_all('tr')
    cleaned_rows = [clean_row(row) for row in table_rows]

    # Delete blank rows at the top
    while not any(cleaned_rows[0]):
        cleaned_rows.pop(0)

    return pd.DataFrame(cleaned_rows)
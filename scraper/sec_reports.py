"""This module holdings the 'Report' class and various other classes related to storing and manipulating the data
    scraped from the sec website.

Things to do:
1. Figure out why the encoding gets all weird when I try to save the html to a file on my computer
2. Refactor everything to make it all better.
3. Update the below to make it more generic. Incorporate not just 10-ks.
4. Thing of a better name for this file

Questions:
 -I am thinking about saving the excel file in the current directory, loading the data into pandas dataframes,
    and then deleting the excel doc after grabbing the info. Better way to do that?
"""

from bs4 import BeautifulSoup
from bs4.element import Tag
import time
from dateutil.parser import parse
from pathlib import Path
import unicodedata
import re
import pandas as pd
import requests

import scraper.scrapefunctions as sp

SEARCH_ROOT = r'https://www.sec.gov/cgi-bin/browse-edgar?'  # Used to build the search url
SEC_DATA_ROOT = 'https://www.sec.gov/'  # Used to build the 10k report url
EXCEL_REPORT_ROOT = 'https://www.sec.gov/Archives/edgar/data/'  # Used to build the excel report url
cik_df: pd.DataFrame = sp.load_ciks()  # load ciks in a panda dataframe for easy lookup later.


def build_search_url(cik, action='getcompany', doc_type='', date_before='', count=10, output='atom'):
    """Function used to build the url for searching edgar.
     -Only necessary input is the cik.
     -date_before should be in format of 'YYYYMMDD'
     -If you don't want the output to come as the rss feed then just put 'output' argument to an empty string
     -Output minimum on the feed is 10 so you will always receive back at least 10 entries.
     """
    query_string = f'action={action}&CIK={cik}&type={doc_type}&dateb={date_before}&count={count}&output={output}'
    return SEARCH_ROOT + query_string


def get_cik(ticker: str):
    """Returns the cik, given a ticker string."""
    return cik_df[cik_df.ticker == ticker].cik.iloc[0]


class Report:
    """This class is used to hold info for a specific report. Right now it is sort of just built for a 10-k"""

    def __init__(self, ticker, report_type, accession_number=None, index_link=None, report_link=None, report_date=None):

        # This group all has the potential to be set as the class is instantiated.
        self.accession_number = accession_number
        self.index_link = index_link
        self.report_link = report_link
        self.report_date = report_date
        self.ticker = ticker
        self.report_type = report_type

        # These will never be set on creation
        self.report_soup = None
        self.excel_link = None
        self.balance_sheet = None
        self.income_statement = None
        self.cash_flow_statement = None

    @property
    def statements(self):
        """Return a list of the essential statements. Should I make it so that it only returns statements with data?"""
        statements = [self.balance_sheet, self.income_statement, self.cash_flow_statement]
        return statements

    @property
    def cik(self):
        """Returns the cik, or raises an exception if there is no ticker. But honestly you can't instanitate this class
            without inputing a ticker so it should always return a ticker"""
        if self.ticker:
            return cik_df[cik_df.ticker == self.ticker].cik.iloc[0]
        else:
            Exception(f'Sorry, this report must have a ticker to look up the cik number.')

    def get_excel_link(self):
        """Retrieves the link to the excel document that contains all the financial info. Must have accession number."""
        if self.accession_number:
            # URL link fore the excel document does not have any '-' in it
            return f'{EXCEL_REPORT_ROOT}{self.cik}/{self.accession_number.replace("-", "")}/Financial_Report.xlsx'
        else:
            Exception('Sorry, you must have the accession_number in order to build the excel_link.')

    def get_excel_response(self):
        """Get's the response of the excel document link."""
        return requests.get(self.get_excel_link())

    def scrape_index_page(self):
        """Extract info from the report index page. Includes: date of report and the report link."""
        # Should probably break this down into multiple sub functions.
        if self.index_link:
            index_soup = sp.get_soup(self.index_link)
            if index_soup:
                # Below assuming it will always be the first table. Safe assumption? Probably not, but it hasn't failed.
                report_table = index_soup.find('table')
                for row in report_table.find_all('tr'):
                    cols = row.find_all(['th', 'td'])
                    # The url is in the 3rd cell and the doc type is in the 4th
                    document_type = cols[3].get_text().lower()
                    # Below ignores report amendments
                    if document_type == self.report_type.lower():
                        document_link = cols[2].find('a')
                        if document_link:
                            document_link = document_link.get('href')
                            # Get rid of the ix part which would take you to the interactive document
                            # We just want the raw html
                            document_link = document_link.replace('/ix?doc=/', '')
                            self.report_link = SEC_DATA_ROOT + document_link
                        break

                # Get the date of the report and convert it to datetime.date
                try:
                    report_date = index_soup.find(string='Period of Report').parent.find_next_sibling().get_text()
                    self.report_date = parse(report_date).date()
                except:
                    print(f'Sorry, could not get the date for {self.index_link}')

    def get_report_soup(self) -> BeautifulSoup:
        """Returns beautiful soup object of the report"""
        report_soup = sp.get_soup(self.report_link)
        return report_soup

    def load_report_soup(self):
        """Store's the report soup in a variable of this instance"""
        self.report_soup = self.get_report_soup()

    def extract_financial_data(self, statements_list: list):
        """Send in a list of the statements you want to extract and this method will hopefully go scrape the data
            and put it into the relevant class variable. The statements should be classes like 'IncomeStatement'"""

        report_soup = self.get_report_soup()

        for statement in statements_list:
            new_statement = statement()
            new_statement.clean_and_extract_data(report_soup)
            if statement.__name__ == 'BalanceSheet':
                self.balance_sheet = new_statement
            elif statement.__name__ == 'IncomeStatement':
                self.income_statement = new_statement
            elif statement.__name__ == 'CashFlowStatement':
                self.cash_flow_statement = new_statement

    def __repr__(self):
        # if self.report_date is not None:
        return f'{self.ticker}: {str(self.report_date)}'


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
            ten_k = Report(ticker=ticker, report_type='10-k', index_link=entry.find('filing-href').get_text(),
                           accession_number=entry.find('accession-number').get_text())
            # Get report link and date off of index page
            ten_k.scrape_index_page()
            all_reports[ticker].append(ten_k)
            time.sleep(.1)  # Small sleep between each url request so that I am not being a dick to Edgar's server.

    return all_reports


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


def clean_row(row_soup: Tag) -> list:
    """Send in a list and return a cleaner list. This method is  real sketchy though and will need refining and
    testing """
    # The goal is to make sure each row only has three columns. The loop should delete any cell that is not an
    # account description or number or hyphen ( which indicates 0 usually)

    # Below converts some weird blank strings into normal blank python strings
    cols = row_soup.find_all('td')
    row = [unicodedata.normalize("NFKD", col.get_text()) for col in cols]

    # Don't get stuck in an infinite loop. Just in case my cleaning doesn't trim everything down enough
    # This whole function just feels like shitty logic. And only makes sense if you are staring at the html of a 10-k.
    max_loop_count = 40
    loop_count = 0
    while len(row) > 3 and loop_count < max_loop_count:
        loop_count += 1
        for col_index, col in enumerate(row):
            if not re.search('[\w-]', col):  # Don't delete a letter, number or hyphen
                if col_index != 0:  # Don't delete the cell in the first column. This isn't the best logic
                    row.pop(col_index)
                    break
    return row


class BalanceSheet:
    """This class will hold the data relevant to the balance sheet on the 10-k."""

    name = 'BalanceSheet'
    keywords = ['assets', 'currents assets', "STOCKHOLDERS' EQUITY", 'Retained earnings', 'Current liabilities',
                'Accounts payable']
    keywords = [keyword.lower() for keyword in keywords]

    def __init__(self):
        self._data_table = None

    @property
    def data_table(self) -> pd.DataFrame:
        return self._data_table

    def clean_and_extract_data(self, report_soup: BeautifulSoup):
        bs_table = get_balance_sheet_table(report_soup)
        if bs_table:
            table_rows = bs_table.find_all('tr')
            cleaned_rows = [clean_row(row) for row in table_rows]

            # Delete blank rows at the top
            while not any(cleaned_rows[0]):
                cleaned_rows.pop(0)

            self._data_table = pd.DataFrame(cleaned_rows)


class IncomeStatement:
    """This class will hold the data relevant to the income statement on the 10-k."""

    name = 'IncomeStatement'
    keywords = ['Interest expense', 'NET INCOME', "REVENUES", 'Depreciation', 'DILUTED', 'BASIC', 'TAXES']
    keywords = [keyword.lower() for keyword in keywords]

    def __init__(self):
        self._data_table = None

    @property
    def data_table(self) -> pd.DataFrame:
        return self._data_table

    def clean_and_extract_data(self, report_soup: BeautifulSoup):
        """Note this does not yet work reliably."""
        is_table = get_income_statement_table(report_soup)
        if is_table:
            table_rows = is_table.find_all('tr')
            cleaned_rows = [clean_row(row) for row in table_rows]

            # Delete blank rows at the top
            while not any(cleaned_rows[0]):
                cleaned_rows.pop(0)

            self._data_table = pd.DataFrame(cleaned_rows)


class CashFlowStatement:
    """This class will hold the data relevant to the cash flow statement on the 10-k."""

    name = 'CashFlowStatement'
    keywords = ['Cash used in financing activities', 'Cash generated by operating activities',
                "investing activities", 'Proceeds from issuance of common stock', 'Repurchases of common stock',
                'Investing activities',  'Cash used for', 'Cash provided by operations',
                'Cash and equivalents at beginning of year', 'CASH FLOWS FROM',
                'CASH AND CASH EQUIVALENTS AT BEGINNING', 'CASH AND CASH EQUIVALENTS']

    keywords = [keyword.lower() for keyword in keywords]

    def __init__(self):
        self._data_table = None

    @property
    def data_table(self) -> pd.DataFrame:
        return self._data_table

    def clean_and_extract_data(self, report_soup: BeautifulSoup):
        """Note this does not yet work reliably."""
        cf_table = get_cash_flow_statement_table(report_soup)
        if cf_table:
            table_rows = cf_table.find_all('tr')
            cleaned_rows = [clean_row(row) for row in table_rows]

            # Delete blank rows at the top
            while not any(cleaned_rows[0]):
                cleaned_rows.pop(0)

            self._data_table = pd.DataFrame(cleaned_rows)


def get_income_statement_table(report_soup: BeautifulSoup):
    """Return income statement table tag soup"""
    """Note this does not yet work reliably."""
    # Grab all the tables that might be the relevant statement
    matched_tables = report_soup.find_all(locate_potential_income_statement_tables)
    if matched_tables:
        return get_most_likely_table(matched_tables, keywords=IncomeStatement.keywords)
    else:
        return None


def locate_potential_income_statement_tables(tag: Tag, match_threshold: int = 3) -> bool:
    """Note this does not yet work reliably."""
    if tag.name == 'table':
        tag_text = tag.get_text().lower()
        matches_count = sum([keyword in tag_text for keyword in IncomeStatement.keywords])
        return matches_count >= match_threshold
    else:
        return False


def get_most_likely_table(tables: list, keywords: list) -> Tag:
    """Return the table that has the most keyword matches"""
    if len(tables) == 1:
        return tables[0]
    else:
        best_table = None
        highest_match_count = 0
        # Now pick the table with the most keyword similarities
        for table in tables:
            match_count = get_match_count(table, keywords)
            if match_count > highest_match_count:
                highest_match_count = match_count
                best_table = table
        return best_table


def get_match_count(tag: Tag, keywords: list):
    """Send in a tag and keyword list and return the number of keywords that were inside the tag test"""
    table_text = tag.get_text().lower()
    matches_count = sum([keyword in table_text for keyword in keywords])
    return matches_count


def get_balance_sheet_table(report_soup: BeautifulSoup) -> Tag:
    """Returns table tag that contains the balance sheet"""

    # Grab all the tables that might be the relevant statement
    matched_tables = report_soup.find_all(locate_potential_balance_sheet_tables)
    if matched_tables:
        return get_most_likely_table(matched_tables, keywords=BalanceSheet.keywords)
    else:
        return None


def get_cash_flow_statement_table(report_soup: BeautifulSoup) -> Tag:
    """Return cash flow statement table tag soup"""
    """Note this does not yet work reliably."""
    # Grab all the tables that might be the relevant statement
    matched_tables = report_soup.find_all(locate_potential_cash_flow_statement_tables)
    if matched_tables:
        return get_most_likely_table(matched_tables, keywords=CashFlowStatement.keywords)
    else:
        return None


def locate_potential_balance_sheet_tables(tag: Tag, match_threshold: int = 3) -> bool:
    """Should locate the balance sheet header. Does so by looking for a certain amount of keywords in the table and
        checking to see if the percentage of keywords is greater than the threshold.
    """
    # Should update this so that the user can input their own list of keywords?
    # Perhaps make this a nested function inside of a more general one to locate any financial statement?
    # Each statement having its own sub function and default keywords?

    # Basically this looks at each table and returns a match if the table contains enough of the keywords.

    if tag.name == 'table':
        tag_text = tag.get_text().lower()
        matches_count = sum([keyword in tag_text for keyword in BalanceSheet.keywords])
        return matches_count >= match_threshold
    else:
        return False


def locate_potential_cash_flow_statement_tables(tag: Tag, match_threshold: int = 3) -> bool:
    """Note this does not yet work reliably."""
    if tag.name == 'table':
        tag_text = tag.get_text().lower()
        matches_count = sum([keyword in tag_text for keyword in CashFlowStatement.keywords])
        return matches_count >= match_threshold
    else:
        return False

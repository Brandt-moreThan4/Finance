"""Things to do:
"""

from pathlib import Path
import pandas as pd

import scraper.report as rp

# TICKERS = ['LUV', 'SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
TICKERS = ['LUV']


# This Script should just go through each of the tickers and extract the data from their balance sheets on their
# two most recent 10-ks and export it to a csv file in the Balance Sheets folder.
# The bulk of the code is in the 'reports.py' file.


url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000092380&type=10-k&dateb=&owner=exclude&count=40&search_text='
import requests

url = 'https://www.sec.gov/Archives/edgar/data/92380/000009238021000033/Financial_Report.xlsx'

response = requests.get(url, 'shoo.xlsx')

with open('test.xlsx', 'wb') as f:
    f.write(response.content)



def main():
    reports = rp.scoop_reports(TICKERS, report_count=1)
    for ticker in reports:
        for report in reports[ticker]:
            statements = (rp.BalanceSheet(), rp.IncomeStatement())
            report.extract_financial_data(statements)
            file_path = Path().cwd() / 'BalanceSheets' / f'{report.ticker}_{report.report_date}.csv'
            if not file_path.parent.exists():
                file_path.parent.mkdir()
            # bs_df.to_csv(file_path)


main()
print("LOL. Done. Isn't that cray!")

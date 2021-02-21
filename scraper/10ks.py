"""Things to do:
1. Figure out why the encoding gets all weird when I try to save the html to a file on my computer
2. refactor everything to make it all better.
3. Prolly a bunch of other stuff.

My Idea for locating statements:
    Use multiple methods to try to locate the html table. If they all agree then boo ya. Otherwise then maybe just don't scrape it?
    Clean all table data before deciding which one is the correct one?
"""

from pathlib import Path
import pandas as pd

import scraper.report as rp

# TICKERS = ['LUV', 'SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
TICKERS = ['LUV']


# This Script should just go through each of the tickers and extract the data from their balance sheets on their
# two most recent 10-ks and export it to a csv file in the Balance Sheets folder.
# The bulk of the code is in the 'reports.py' file.

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
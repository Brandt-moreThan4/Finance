"""
This module is just used test and play around with the functionality of the sec_reports file.
"""

from pathlib import Path
import pandas as pd

import scraper.sec_reports as rp

# TICKERS = ['LUV', 'SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
TICKERS = ['LUV', 'AAPL']


# This Script should just go through each of the tickers and extract the data from their balance sheets on their
# three most recent 10-ks and export it to a csv file in the Balance Sheets folder.
# The bulk of the code is in the 'sec_reports.py' file.

def main():
    reports = rp.scoop_reports(TICKERS, report_count=3)
    for ticker in reports:
        for report in reports[ticker]:
            statements = (rp.BalanceSheet(),)
            report.extract_financial_data(statements)
            file_path = Path().cwd() / 'BalanceSheets' / f'{report.ticker}_{report.report_date}.csv'
            for statement in report.statements:
                statement.data_table.to_csv(file_path)


if __name__ == '__main__':
    main()
    print("LOL. Done. Isn't that cray!")

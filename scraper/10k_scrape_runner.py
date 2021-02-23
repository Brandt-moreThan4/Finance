"""
This module is just used test and play around with the functionality of the sec_reports file.
"""

from pathlib import Path
import pandas as pd

import scraper.sec_reports as rp

# TICKERS = ['LUV', 'SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
TICKERS = ['LUV', 'AAPL']


# This Script should just go through each of the tickers and extract the data from their balance sheets and income
# statement on their three most recent 10-ks and export it to a csv file in the Financial Statements folder
# The bulk of the code is in the 'sec_reports.py' file.

def main():
    reports = rp.scoop_reports(TICKERS, report_count=3)
    file_path = Path().cwd() / 'FinancialStatements'
    for ticker in reports:
        for report in reports[ticker]:
            statements = (rp.BalanceSheet, rp.IncomeStatement)
            report.extract_financial_data(statements)
            for statement in report.statements:
                if statement and statement.data_table is not None:
                    file_path = Path().cwd() / 'FinancialStatements'
                    file_path = file_path / f'{report.ticker}_{report.report_date}_{statement.name}.csv'
                    statement.data_table.to_csv(file_path)


if __name__ == '__main__':
    main()
    print("LOL. Done. Isn't that cray!")

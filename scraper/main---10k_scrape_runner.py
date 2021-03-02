"""
This module is just used test and play around with the functionality of the sec_reports file.
"""

"""
This Script should just go through each of the tickers and extract the data from their balance sheets, 
income statement, and cash flow statement on their two most recent 10-ks and export it to a csv file in the 
Financial Statements folder. The bulk of the code is in the 'sec_reports.py' file.

It still needs heavy refining. Does not always pull the correct table from the report and sometimes misses columns of
data.
"""

from pathlib import Path

import scraper.sec_reports as rp

TICKERS = ['LUV', 'SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
# TICKERS = ['LUV']


def main():
    reports = rp.scoop_reports(TICKERS, report_count=2)  # In this usage, the report_count argument equals years to pull
    for ticker in reports:
        for report in reports[ticker]:
            statements = (rp.BalanceSheet, rp.IncomeStatement, rp.CashFlowStatement)
            report.extract_financial_data(statements)
            for statement in report.statements:
                if statement and statement.data_table is not None:
                    file_path = Path().cwd() / 'FinancialStatements'
                    file_path = file_path / f'{report.ticker}_{report.report_date}_{statement.name}.csv'
                    statement.data_table.to_csv(file_path)


if __name__ == '__main__':
    main()

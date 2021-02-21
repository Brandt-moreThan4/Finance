"""Things to do:
"""

from pathlib import Path
import pandas as pd

import scraper.report as rp
import pandas as pd
# TICKERS = ['LUV', 'SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
TICKERS = ['LUV', 'SBUX', 'CMG']

# This Script should just go through each of the tickers and extract the data from their balance sheets on their
# two most recent 10-ks and export it to a csv file in the Balance Sheets folder.
# The bulk of the code is in the 'reports.py' file.

import requests

# url = 'https://www.sec.gov/Archives/edgar/data/92380/000009238021000033/Financial_Report.xlsx'
EXCEL_REPORT_ROOT = 'https://www.sec.gov/Archives/edgar/data/'


def main():
    reports = rp.scoop_reports(TICKERS, report_count=1)
    for ticker in reports:
        for report in reports[ticker]:
            url = report.get_excel_link()
            response = requests.get(url)
            df = pd.DataFrame(response.content)
            # file_path = Path().cwd() / 'excel_reports' / report.ticker / f'Financials_{report.report_date}.xlsx'
            # if not file_path.parent.exists():
            #     file_path.parent.mkdir()
            # with file_path.open(mode='wb') as f:
            #     f.write(response.content)


main()
print("LOL. Done. Isn't that cray!")

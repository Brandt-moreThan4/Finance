"""This module is just used test and play around with the functionality of the sec_reports file.
"""

from pathlib import Path

import scraper.sec_reports as rp

# TICKERS = ['LUV', 'SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
TICKERS = ['LUV', 'SBUX']


# This script will just pull the full financial statement data from the edgar website into an excel file to put
# into the folder'excel reports'
def main():
    reports = rp.scoop_reports(TICKERS, report_count=2)
    for ticker in reports:
        for report in reports[ticker]:
            response_content = report.get_excel_response().content
            file_path = Path().cwd() / 'excel_reports' / f'Financials_{report.ticker}_{report.report_date}.xlsx'
            with file_path.open(mode='wb') as f:
                f.write(response_content)


if __name__ == '__main__':
    main()
print("LOL. Done. Isn't that cray!")

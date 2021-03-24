"""
Update the readme. add pictures
Currenttly we only find exact matches. Reduces false positive rate, but also reduces true positive rate.
I should probably never use the count function since it will also include extensions of the word that are not
exact matches.
Things to do:
-Remove punctuation from word lists. Or instead of cleaning words, make the word detector more forgiving
-figure out how to handle when the paragraph is split across pages.
"""

from pathlib import Path

import scraper.sec_reports as rp
import pandas as pd

from scraper.parser_settings import *
import scraper.helper_funcs as hp
import time



# Returns a dictionary where key is ticker and values are a list of reports for the amount of years specified
ten_k_reports_dict = rp.scoop_reports(TICKERS, YEARS)

all_text_chunks = []
master_table = []
skipped_reports = []
for ticker, reports in ten_k_reports_dict.items():
    for ten_k in reports:
        if ten_k.report_link is not None: # Ignore reports that don't have links.
            ten_k.load_report_soup()
            # time.sleep(.2)
            text_chunks = hp.get_text_chunks(ten_k.report_soup)
            for paragraph_number, text_chunk in enumerate(text_chunks):
                paragraph = hp.TextChunk(text_chunk)
                all_text_chunks.append(paragraph)
                matches = ';'.join([match.word for match in paragraph.matches])
                row = [ticker, ten_k.report_date, paragraph_number, matches, paragraph.text, ten_k.report_link, ten_k.index_link]
                master_table.append(row)
        else:
            skipped_reports.append((ticker, ten_k.report_date, ten_k.report_link))

print(skipped_reports)

df = pd.DataFrame(master_table)
DATA_FRAME_COLUMNS = ['ticker', 'report_date', 'paragraph_number', 'matches', 'para_text', 'report_link', 'report_index']
df.columns = DATA_FRAME_COLUMNS

df.to_excel('paragraphs.xlsx')
print('lol')

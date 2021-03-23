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






# DATA_FRAME_COLUMNS = ['report_date', 'ticker', 'p_number', 'p_text']
# DATA_FRAME_COLUMNS.extend(ALL_WORDS)



# Returns a dictionary where key is ticker and values are a list of reports for the amount of years specified
ten_k_reports_dict = rp.scoop_reports(TICKERS, YEARS)

all_text_chunks = []
master_table = []
for ticker, reports in ten_k_reports_dict.items():
    for ten_k in reports:
        ten_k.load_report_soup()
        # Get the text from each 'div' element in the 10k's html and convert it to all lower case
        text_chunks = hp.get_text_chunks(ten_k.report_soup)
        # text_chunks: list = [div.get_text().lower() for div in ten_k.report_soup.find_all('div')]
        for paragraph_number, text_chunk in enumerate(text_chunks):
            paragraph = hp.TextChunk(text_chunk)
            all_text_chunks.append(paragraph)
            matches = ';'.join([match.word for match in paragraph.matches])
            row = [ticker, ten_k.report_date, paragraph_number, matches, paragraph.text, ten_k.report_link]
            master_table.append(row)

print('lol')

df = pd.DataFrame(master_table)
DATA_FRAME_COLUMNS = ['ticker', 'report_date', 'paragraph_number', 'matches', 'para_text', 'report_link']
df.columns = DATA_FRAME_COLUMNS

df.to_excel('paragraphs.xlsx')
print('lol')

# def main():

# if __name__ == '__main__':
#     main()

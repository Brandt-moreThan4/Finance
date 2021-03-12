"""This is hard
"""

from pathlib import Path

import scraper.sec_reports as rp
import pandas as pd
import numpy as np
import math

# TICKERS = ['LUV', 'SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
TICKERS = ['LUV']
YEARS = 1

HEDGING_WORDS = ['derivatives', 'futures', 'forwards', 'options', 'hedge']
OFFSHORING_WORDS = ['supplier', 'export', 'import']
NATION_WORDS = []
ALL_WORDS = HEDGING_WORDS + OFFSHORING_WORDS + NATION_WORDS

DATA_FRAME_COLUMNS = ['report_date', 'ticker', 'p_number', 'p_text']
DATA_FRAME_COLUMNS.extend(ALL_WORDS)


class TextChunk:

    def __init__(self):
        self.text: str = None
        self.hedging_word_count = None
        self.offshoring_word_count = None
        self.nation_words_count = None

    # def load_key_word_counts(self):
    #     self.hedging_word_count =


def get_word_index(word_list: list, search_word: str):
    """This should always return an index because it should only be used when you know the search word is somewhere
    in the list. Slightly different from using list.index because this will return a match if the word is somewhere
    inside the list value, not just an exact match"""

    for index, word in enumerate(word_list):
        if search_word in word:
            return index


def get_nearest_neighbor_words(text: str, search_word: str, neighbor_count: int):
    """Will only get the first occurrence. This really needs some heavy testing. Would love to know easier ways
     to do this"""

    left_words_goal = math.floor(neighbor_count / 2)
    right_words_goal = math.ceil(neighbor_count / 2)

    if search_word not in text:
        return []
    else:
        # This is so convoluted. Got to be a better way to do this.
        words_list = text.split(' ')
        word_count = len(words_list)
        word_index_in_list = get_word_index(words_list, search_word)
        total_words_left = word_index_in_list
        total_words_right = word_count - word_index_in_list

        left_neighbor_count = min(total_words_left, left_words_goal)
        right_neighbor_count = min(total_words_right, right_words_goal)
        total_neighbors = left_neighbor_count + right_neighbor_count

        spare_words_left = max(0, total_words_left - left_neighbor_count)
        spare_words_right = max(0, total_words_right - right_neighbor_count)
        total_spare_words = spare_words_left + spare_words_right

        # If one of the sides does not have
        if total_neighbors < neighbor_count and total_spare_words > 0:

            if left_neighbor_count < left_words_goal and spare_words_right > 0:
                words_to_add_right = min(left_words_goal - left_neighbor_count, spare_words_right)
                right_neighbor_count += words_to_add_right
                total_neighbors = words_to_add_right
            elif right_neighbor_count < right_words_goal and spare_words_left > 0:
                words_to_add_left = min(right_words_goal - right_neighbor_count, spare_words_left)
                left_neighbor_count += words_to_add_left
                total_neighbors += words_to_add_left

        words_index_start = word_index_in_list - left_neighbor_count
        words_index_end = word_index_in_list + right_neighbor_count + 1
        nearest_neighbors = words_list[words_index_start:word_index_in_list] + \
                            words_list[word_index_in_list+1:words_index_end]

        return nearest_neighbors


# Returns a dictionary where key is ticker and values are a list of reports for the amount of years specified
ten_k_reports_dict = rp.scoop_reports(TICKERS, YEARS)

master_table = []
for ticker, reports in ten_k_reports_dict.items():
    for ten_k in reports:
        ten_k.load_report_soup()
        # Get the text from each 'div' element in the 10k's html and convert it to all lower case
        paragraphs: list = [div.get_text().lower() for div in ten_k.report_soup.find_all('div')]
        for paragraph_number, paragraph in enumerate(paragraphs):
            # This is a bit convoluted
            table_row = []
            table_row.extend([paragraph_number, ten_k.report_date, ticker])
            word_counts = [paragraph.count(word) for word in ALL_WORDS]
            table_row.extend(word_counts)
            table_row.append(paragraph)

            master_table.append(table_row)

df = pd.DataFrame(master_table)
df.columns = DATA_FRAME_COLUMNS

# df.to_excel('paragraphs.xlsx')
print('lol')

# def main():

# if __name__ == '__main__':
#     main()

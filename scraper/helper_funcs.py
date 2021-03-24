import math
from scraper.parser_settings import *
from bs4 import BeautifulSoup
from bs4 import Tag


# def get_word_index(word_list: list, search_word: str) -> tuple:
#     """This should always return an index because it should only be used when you know the search word is somewhere
#     in the list. Slightly different from using list.index because this will return a match if the word is somewhere
#     inside the list value, not just an exact match. Also returns a tuple of the each index."""
#
#     word_indexes = []
#     for index, word in enumerate(word_list):
#         if search_word in word:
#             word_indexes.append(index)
#
#     return tuple(word_indexes)
#
#
# def contains(container, search_term: str):
#     for thing in container:
#         if search_term in thing:
#             return True
#     return False


def clean_word_chunk(word: str, characters_to_remove: list) -> str:
    """Clean that chunk"""
    cleaned_word = word
    for character in characters_to_remove:
        cleaned_word = cleaned_word.replace(character, '')
    return cleaned_word


def get_nearest_neighbor_words(words_list: list, word_index: int, neighbor_count: int):
    """This really needs some heavy testing. Would love to know easier ways
     to do this"""

    left_words_goal = math.floor(neighbor_count / 2)
    right_words_goal = math.ceil(neighbor_count / 2)

    # This is so convoluted. Got to be a better way to do this.
    word_count = len(words_list)

    total_words_left = word_index
    total_words_right = word_count - word_index

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

    first_neighbor_index = word_index - left_neighbor_count
    last_neighbor_index = word_index + right_neighbor_count + 1
    nearest_neighbors = words_list[first_neighbor_index:word_index] + \
                        words_list[word_index + 1:last_neighbor_index]

    return nearest_neighbors


class MatchedWord:

    def __init__(self, word: str, neighbors_list: list):
        self.word = word
        self.neighbors_list = neighbors_list
        self.neighbor_text = ' '.join(self.neighbors_list)
        self.sub_matches = []
        self.find_neighbor_matches()

    def find_neighbor_matches(self):
        # self.sub_matches = {}
        for word in self.neighbors_list:
            if word in all_words_dict:
                self.sub_matches.append(word)

    def __str__(self):
        return self.word

    def __repr__(self):
        return self.word


class TextChunk:
    """This will most likely be a class used to represent a single paragraph's chunk of text."""

    # CHARACTERS_TO_REMOVE = [';', ',', '.', '!', '?']

    def __init__(self, text: str):
        self.text: str = text
        self.word_list = [clean_word_chunk(word, CHARACTERS_TO_REMOVE) for word in text.split(' ')]
        # self.load_key_word_counts()
        # self.hedging_word_count_total = sum(self.hedging_word_counts.values())
        # self.offshoring_word_count_total = sum(self.offshoring_word_counts.values())
        # self.nation_words_count_total = sum(self.nation_word_counts.values())
        # self.total_word_count = self.hedging_word_count_total + self.nation_words_count_total \
        #                         + self.offshoring_word_count_total
        self.matches = []
        self.load_matches()

    # def load_key_word_counts(self):
    #     """These may over count the actual word count."""
    #     self.hedging_word_counts = {key: value for (key, value) in
    #                                 zip(HEDGING_WORDS, [self.text.count(word) for word in HEDGING_WORDS])}
    #     self.offshoring_word_counts = {key: value for (key, value) in
    #                                    zip(OFFSHORING_WORDS, [self.text.count(word) for word in OFFSHORING_WORDS])}
    #     self.nation_word_counts = {key: value for (key, value) in
    #                                zip(NATION_WORDS, [self.text.count(word) for word in NATION_WORDS])}

    def load_matches(self):
        """Look at all the words in the text chunk. If there is a match, then create a MatchedWord object object."""
        for index, word in enumerate(self.word_list):
            if word in all_words_dict:
                match = MatchedWord(word, get_nearest_neighbor_words(self.word_list, index, neighbor_count=25))
                self.matches.append(match)

    def __repr__(self):
        return str(self.matches)


def use_divs(report_soup:BeautifulSoup):

    divs = report_soup.find_all('div')
    paragraphs = report_soup.find_all('p')
    if len(divs) > len(paragraphs):
        return True
    else:
        return False


def get_text_chunks(report_soup: BeautifulSoup):
    """Send in report soup and hopefully returns a list which will contain all of the paragraphs in the report. """
    # Basically just captures all of the top level div elements excluding the ones that contain table elemenets.
    # First get divs

    if use_divs(report_soup):
        element_list = report_soup.find_all('div')
    else:
        element_list = report_soup.find_all('p')

    text_chunk_soups = []
    for element in element_list:
        if element.find_parent('table') is None:  # Only add to the list if the soup does not have a table ancestor
            text_chunk_soups.append(element)
    text_chunks = [element.get_text().lower() for element in text_chunk_soups]

    return text_chunks


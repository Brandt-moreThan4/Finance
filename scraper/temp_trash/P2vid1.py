url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000092380&type=10-k&dateb=&owner=exclude&count=40&search_text='

import re
import requests
import unicodedata
from bs4 import BeautifulSoup

import scraper.scrapefunctions as sp

# define the url to specific html_text file
new_html_text = r"https://www.sec.gov/Archives/edgar/data/1166036/000110465904027382/0001104659-04-027382.txt"

# grab the response
response = requests.get(new_html_text)

# pass it through the parser, in this case let's just use lxml because the tags seem to follow xml.
soup = BeautifulSoup(response.content, 'lxml')

# daddy dict to hold all filings
master_filings_dict = {}

# make sure below is unique?
accession_number = '0001104659-04-027382'

master_filings_dict[accession_number] = {}
master_filings_dict[accession_number]['sec_header_content'] = {}
master_filings_dict[accession_number]['filing_documents'] = None

sec_header_tag = soup.find('sec_header')
# store header content in dictionary
master_filings_dict[accession_number]['sec_header_content']['sec_header_code'] = sec_header_tag

master_document_dict = {}

for filing_document in soup.find_all('document'):
    document_id = filing_document.type.find(text=True, recursive=False).strip()
    document_sequence = filing_document.sequence.find(text=True, recursive=False).strip()
    document_filename = filing_document.filename.find(text=True, recursive=False).strip()
    document_description = filing_document.description.find(text=True, recursive=False).strip()

    master_document_dict[document_id] = {}
    master_document_dict['document_sequence'] = document_sequence
    master_document_dict['document_filename'] = document_filename
    master_document_dict['document_description'] = document_description

    master_document_dict[document_id]['document_code'] = filing_document.extract()

    filing_doc_text = filing_document.find('text').extract()

    # Is below still work for current html patterns?
    all_thematic_breaks = filing_doc_text.find_all('hr', {'width': '100%'})


    #strings
    all_thematic_breaks = [str(thematic_break) for thematic_break in all_thematic_breaks]
    filing_doc_string = str(filing_doc_text)

    if len(all_thematic_breaks) > 0:
        regex_delimited_pattern = '|'.join(map(re.escape, all_thematic_breaks))
        split_filing_string = re.split(regex_delimited_pattern, filing_doc_string)
        master_document_dict[document_id]['pages_code'] = split_filing_string
    else:
        master_document_dict[document_id]['pages_code'] = [filing_doc_string]

filing_documents = master_filings_dict[accession_number]['filing_documents']




print('lol')

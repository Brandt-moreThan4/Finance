
import pandas as pd
import scraper.scrapefunctions as sp

root_path = r'C:\Users\15314\OneDrive\Desktop\Filings'


# df = pd.read_csv(root_path + '\\num.tsv', sep='\t')

df = sp.load_ciks()
print('lol')
# TICKERS = ['LUV', 'SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
TICKERS = ['LUV', 'AAL', 'DAL', 'UAL', 'ALK', 'JBLU', 'SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']
# TICKERS = ['UAL']
YEARS = 10

HEDGING_WORDS = ['derivatives', 'futures', 'forwards', 'options', 'hedge', 'spot', 'swap']
NATION_WORDS = ['china', 'europe', 'mexico', 'canada', 'asia', 'japan', 'india', 'argentina']

OFFSHORE_INTERNAL_INPUT_WORD = ['factory', 'plant', 'facility']
OFFSHORE_EXTERNAL_INPUT_WORDS = ['supplier', 'vendor', 'subcontract']
OFFSHORE_OUTPUT_WORDS = ['sell', 'export', 'distribute']
OFFSHORE_INDETERMINATE_WORDS = ['supplier', 'export', 'import']

hedge_dict = {word: 'hedge' for word, value in zip(HEDGING_WORDS, range(len(HEDGING_WORDS)))}

nation_dict = {word: 'nation' for word, value in zip(NATION_WORDS, range(len(NATION_WORDS)))}
internal_input_dict = {word: 'internal_input' for word, value in
                       zip(OFFSHORE_INTERNAL_INPUT_WORD, range(len(OFFSHORE_INTERNAL_INPUT_WORD)))}
external_input_dict = {word: 'external_input' for word, value in
                       zip(OFFSHORE_EXTERNAL_INPUT_WORDS, range(len(OFFSHORE_EXTERNAL_INPUT_WORDS)))}
output_dict = {word: 'output' for word, value in zip(OFFSHORE_OUTPUT_WORDS, range(len(OFFSHORE_OUTPUT_WORDS)))}
indeterminate_dict = {word: 'indeterminate' for word, value in
                      zip(OFFSHORE_INDETERMINATE_WORDS, range(len(OFFSHORE_OUTPUT_WORDS)))}

all_words_dict = hedge_dict | nation_dict | internal_input_dict | external_input_dict | output_dict | indeterminate_dict

CHARACTERS_TO_REMOVE = [';', ',', '.', '!', '?']
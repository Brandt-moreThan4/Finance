import re

text = """Return an iterator yielding match objects over all non-overlapping matches for the RE pattern in string. 
The string is scanned left-to-right, and matches are returned in the order found. Empty matches are included in the 
result. """



HEDGING_WORDS = ['derivatives', 'futures', 'forwards', 'options', 'hedge', 'spot', 'swap']
NATION_WORDS = ['China', 'Europe', 'Mexico', 'Canada']

OFFSHORE_INTERNAL_INPUT_WORDS = ['factory', 'plant', 'facility']
OFFSHORE_EXTERNAL_INPUT_WORDS = ['supplier', 'vendor', 'subcontract']
OFFSHORE_OUTPUT_WORDS = ['sell', 'export', 'distribute']
OFFSHORE_INDETERMINATE_WORDS = ['supplier', 'export', 'import']

hedge_dict = {word: 'hedge' for word, value in zip(HEDGING_WORDS, range(len(HEDGING_WORDS)))}

nation_dict = {word: 'nation' for word, value in zip(NATION_WORDS, range(len(NATION_WORDS)))}
internal_input_dict = {word: 'internal_input' for word, value in zip(OFFSHORE_INTERNAL_INPUT_WORDS, range(len(OFFSHORE_INTERNAL_INPUT_WORDS)))}

combo = nation_dict | internal_input_dict

external_input_dict = {word: 'external_input' for word, value in OFFSHORE_EXTERNAL_INPUT_WORDS}
output_dict = {word: 'output' for word, value in OFFSHORE_OUTPUT_WORDS}
indeterminate_dict = {word: 'indeterminate' for word, value in OFFSHORE_INDETERMINATE_WORDS}

print('ha')
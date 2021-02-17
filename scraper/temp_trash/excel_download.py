url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000092380&type=10-k&dateb=&owner=exclude&count=40&search_text='

import requests

url = 'https://www.sec.gov/Archives/edgar/data/92380/000009238021000033/Financial_Report.xlsx'

response = requests.get(url, 'shoo.xlsx')


output = open('test.xlsx', 'wb')
output.write(response.content)
output.close()

print('lol')
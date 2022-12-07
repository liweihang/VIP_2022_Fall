import requests
from bs4 import BeautifulSoup

request_data = {
    'page' : '1',
    'sat_name' : "AQUARIUS",
    'gso' : 'true',
    'ngso' : 'true',
    'sup' : 'false',
    'sup_only' : 'false',
    'admin' : '',
    'd_rcv_from' : '',
    'd_rcv_to' : '',
    'd_wic_from' : '',
    'd_wic_to' : '',
    'wic_no' : '',
    'freq_from' : '',
    'freq_to' : '',
    'long_from' : '',
    'long_to' : '',
    'sns_ntc_id' : '',
    'txt_sat_name' : '',
    'year' : '',
    'org_net' : ''
}

request_url = "https://www.itu.int/net4/ITU-R/SpaceWISC/apipub/Home/SearchNotice"

response = requests.post(request_url, request_data)

print(response.status_code)
#print(response.text)

soup = BeautifulSoup(response.text, 'html.parser')

links = soup.find_all('a')
detail_link = None
for link in links:
    if link.get('href') is not None:
        detail_link = link.get('href')

#print(detail_link)
detail_url = "https://www.itu.int" + detail_link
print(detail_url)

response = requests.get(detail_url)
with open('response.html', 'w') as file:
    file.write(response.text)


#!/usr/bin/python3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from config import token

chrome_options=Options()
chrome_options.add_argument('--headless')
#driver=webdriver.Chrome('/opt/WebDriver/bin/chromedriver')
driver=webdriver.Chrome('/usr/bin/chromedriver', options=chrome_options)
driver.get("http://localhost:4040/status")
reqHTML=driver.page_source
#print(reqHTML)
soup = BeautifulSoup(reqHTML, 'html5lib')
table=soup.findChild('table')
#print(table)
rows = table.findChildren(['th', 'tr'])
url=[]
for row in rows:
    cells = row.findChildren('td')
    for cell in cells:
        value = cell.text
        url.append(value)
url=url[0]
#print (url)
turl='https://api.telegram.org/bot'
komand='/setWebhook?url='
setwebhook_url=turl+token+komand+url
print(setwebhook_url)
try:
    pass
    zapr=requests.post(setwebhook_url)
    print(zapr)
except:
    print('error set webhook')
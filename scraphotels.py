from selenium import webdriver 
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime
import requests

driver = webdriver.Chrome("C:\Program Files\Google\Chrome\Application\chromedriver.exe")

models = []
prices = []
driver.get('https://www.google.com/travel/search?q=')

time.sleep(10)
## https://www.google.com/travel/search?q=tokyo

content = driver.page_source

soup = BeautifulSoup(content, features="html.parser")
for element in soup.findAll('div', attrs={'class': 'jVsyI'}):
    hotel = element.find('h2', attrs={'class': 'BgYkof ogfYpf ykx2he'})
    models.append(hotel.text)


df = pd.DataFrame({'Hotel Name': models})
df.to_csv('hotels.csv', index=False, encoding='utf-8')

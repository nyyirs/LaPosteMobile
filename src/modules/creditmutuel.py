# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 11:33:45 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re

response = requests.get('https://www.creditmutuel.fr/fr/particuliers/mobile/forfaits-sans-mobile-prompto.html')

# Ensure BeautifulSoup is used with the response content, specifying 'lxml' as the parser
soup = BeautifulSoup(response.text, 'lxml')  # Use response.text to get the HTML content

names = soup.find_all(class_="card__data")
alt_names = [plan.text.strip() for plan in names if plan.text.strip()]

is5g = soup.find_all(class_="card__speed")
pattern_5g = re.compile(r"5G")
extracted_5g = [bool(pattern_5g.search(text.text)) for text in is5g]

price_big_elements = soup.find_all(class_="card__price__big")
price_bis_elements = soup.find_all(class_="card__price__bis")
# Assuming each 'card__price__big' is followed by a 'card__price__bis', we pair them
full_prices = []
for big, bis in zip(price_big_elements, price_bis_elements):
    big_text = big.get_text(strip=True)
    bis_text = bis.div.get_text(strip=True).replace(u'\xa0', u' ').replace("€", "").replace(",",".").replace(" ","")
    full_prices.append(big_text + bis_text)
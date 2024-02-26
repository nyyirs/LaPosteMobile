# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 21:00:46 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re

response = requests.get('https://www.auchantelecom.fr/fr/')

# Ensure BeautifulSoup is used with the response content, specifying 'lxml' as the parser
soup = BeautifulSoup(response.text, 'lxml')  # Use response.text to get the HTML content

names = soup.find_all(class_="data")
alt_names = [plan.text.strip() for plan in names if plan.text.strip()]
filtered_names = [name for name in alt_names if len(name) > 10]

pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
extracted_texts = [pattern.search(text).group(0) for text in filtered_names if pattern.search(text)]

pattern_5g = re.compile(r"5g")
extracted_5g = [bool(pattern_5g.search(text)) for text in filtered_names if text.strip()]

prices = soup.find_all(class_="price")
prices = [item.text.strip() for item in prices if item]
prices_no_duplicates = list(set(prices))[:-1]
prices = [price.replace("€",".").replace("/mois","") for price in prices_no_duplicates]

extracted_data = []

for name, is5g, price in zip(extracted_texts, extracted_5g, prices):
    extracted_data.append((name, is5g, price))
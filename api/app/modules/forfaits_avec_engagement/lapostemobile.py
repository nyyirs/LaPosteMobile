# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 11:35:12 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
import logging

url = 'https://www.lapostemobile.fr/offres-mobiles/forfaits-avec-telephone'
response = requests.get(url)
if response.status_code != 200:
    logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
    raise Exception(f"Failed to fetch data from {url}")
soup = BeautifulSoup(response.content, 'html.parser')

"""Process scraped plan data."""
logging.info("Processing scraped data.")
plans = []
# Extract plan details
names = soup.find_all(id="imgCaracteristique")
prix_entier = soup.find_all(class_="prix_entier")
prix_decimal = soup.find_all(class_="decimal")
prix_5g = soup.find_all(class_="option5g")        
alt_names = [name['alt'] for name in names if name]
formatted_names = [text.replace('<br/>', '\n') for text in alt_names]
pattern = re.compile(r"\b\d+(?:Go|Mo)\b")
pattern_5g = re.compile(r"5G")
extracted_names = [pattern.search(text).group(0) for text in formatted_names if pattern.search(text)]
extracted_5g = [bool(pattern_5g.search(text)) for text in formatted_names if text.strip()]        
alt_prices = [item.text.strip() for item in prix_entier if item]
alt_decimals = [item.text.strip() for item in prix_decimal if item]
alt_prices_5g = [item.text.strip() for item in prix_5g if item]        
plan_prices = []
for text, price, decimal in zip(extracted_names, alt_prices, alt_decimals):
    decimal_part = re.search(r"(\d+)", decimal).group(1) if decimal else ''
    full_price = f"€{price}" + (f".{decimal_part}" if decimal_part else "")
    plan_prices.append(full_price)        
extracted_5g_Add = [int(''.join(filter(str.isdigit, item))) if any(c.isdigit() for c in item) else 0 for item in alt_prices_5g]
if len(extracted_5g) > len(extracted_5g_Add):
    extracted_5g_Add.extend([0] * (len(extracted_5g) - len(extracted_5g_Add)))
for name, is_5g, price, price_addon in zip(extracted_names, extracted_5g, plan_prices, extracted_5g_Add):
    plans.append({'name': name, 'is_5g': is_5g, 'price': price, 'price_addon': price_addon, 'year': 2})


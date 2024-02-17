# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 11:35:12 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
import os
from dotenv import load_dotenv
import pymssql


response = requests.get("https://www.sfr.fr/offre-mobile")  
        
soup = BeautifulSoup(response.content, 'html.parser')

names = soup.find_all(class_="title")
alt_names = [item.text for item in names if item]

pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
extracted_texts = [item for item in alt_names if pattern.search(item)]


pattern_5g = re.compile(r"5G")
extracted_5g = [bool(pattern_5g.search(text)) for text in alt_names if text.strip()]

prix_entier = soup.find_all(class_="L")
prix_decimal = soup.find_all(class_="R")
alt_prices = [item.text.strip() for item in prix_entier if item]
alt_decimals = [item.text.strip() for item in prix_decimal if item]
cleaned_list_decimals = [item for item in alt_decimals if item != '/mois']

plan_prices = {}
for text, price, decimal in zip(extracted_texts[2:], alt_prices[2:], cleaned_list_decimals[2:]):
    if not decimal:
        decimal_part = ''
    else:
        match = re.search(r"(\d+)", decimal)
        decimal_part = match.group(1) if match else ''
    
    full_price = f"€{price}" + (f".{decimal_part}" if decimal_part else "")
    plan_prices[text.replace(" ", "")] = full_price  # Remove spaces to match column names





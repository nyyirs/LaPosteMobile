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


response = requests.get('https://www.sfr.fr/offre-mobile')
soup = BeautifulSoup(response.content, 'html.parser')

names = soup.find_all('li', class_="cinqg")
# Corrected: Removed parentheses from item.text
alt_names = [item.text.split('Client Box')[0] for item in names if '24' in item.text] 

re_data_amount = r"\d{1,3}\sGo"
re_technology = r"5G|4G"
re_price = r"\d{1,3}(?:[.,]\d{2})?\s?€|\d{2},\d{2}€(?:\/mois)?"

extracted_details_dynamic = []

for plan in alt_names:
    data_amount_matches = re.findall(re_data_amount, plan)
    technology_matches = re.findall(re_technology, plan)
    price_matches = re.findall(re_price, plan)
    prices = [price.replace(" ", "").replace("€", "").replace(",", ".") for price in price_matches]

    # Correcting the cents part for prices and dynamically determining the plan duration
    prices_corrected = []
    for price in prices:
        if "." not in price:
            price += ".99"  # Assuming missing cents should be ".99"
        prices_corrected.append(price)

    if data_amount_matches and technology_matches:
        data_amount = data_amount_matches[0]
        technology = technology_matches[0]

        # Dynamically determine if the plan is for 6 or 24 months based on the presence of specific phrases
        # Assuming that the presence of "pendant 6 mois" indicates a 6-months special pricing
        if "pendant 6 mois" in plan:
            # First price is for 6 months, subsequent for 24
            extracted_details_dynamic.append([data_amount, technology, prices_corrected[0], 1])  # 6 months
            for price in prices_corrected[1:]:
                extracted_details_dynamic.append([data_amount, technology, price, 2])  # 24 months
        else:
            # If no specific mention, assume all prices are for 24 months
            for price in prices_corrected:
                extracted_details_dynamic.append([data_amount, technology, price, 2])  # 24 months

extracted_details_dynamic


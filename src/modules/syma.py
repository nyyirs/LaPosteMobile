# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 08:51:34 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re

response = requests.get('https://www.symamobile.com/forfait?fid=294&req=compare')

# Ensure BeautifulSoup is used with the response content, specifying 'lxml' as the parser
soup = BeautifulSoup(response.text, 'lxml')  # Use response.text to get the HTML content

names = soup.find_all("span", class_="red")
# Use a list comprehension with a condition to preserve order and remove duplicates
alt_names = []
[alt_names.append(plan.text.strip().replace(' ', '')) for plan in names if plan.text.strip() and plan.text.strip().replace(' ', '') not in alt_names]

prices = soup.find_all("div", class_="forfaits_top_list_item")
alt_prices = [price.text.strip().replace('\n',' ') for price in prices if price.text.strip()]

network_technology = [True if '5G' in text else False if '4G' in text else None for text in alt_prices][:4]

# Extract the price and replace ' €' with '.'
prices_only = [re.search(r'(\d+)\s€(\d+)', text) for text in alt_prices]
prices_formatted = [f"{match.group(1)}.{match.group(2)}" for match in prices_only if match]

merged_results = list(zip(alt_names, network_technology, prices_formatted))


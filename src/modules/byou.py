# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 14:51:25 2024

@author: nyyir.m.soobrattee
"""

import requests
from bs4 import BeautifulSoup
import json
import re

response = requests.get("https://www.bouyguestelecom.fr/forfaits-mobiles/sans-engagement")  

soup = BeautifulSoup(response.text, 'html.parser')

# Find the <script> tag by ID for JSON data extraction
script_tag = soup.find('script', id='__NEXT_DATA__')

# Extract and parse the JSON string
json_str = script_tag.string if script_tag else '{}'
data = json.loads(json_str)

other_offers = data['props']['pageProps']['productsList']['catalogue']

main_offers = data['props']['pageProps']['productsList']['offers']

extracted_data = []

for offer in main_offers:
    data_envelope = offer['data_envelope']
    newprice = offer['newprice']
    # Determine if option5g is present and has data
    option5g_present = bool(offer['option5g'])

    # Always add the base entry with the actual 5G status
    if option5g_present:
        # If 5G data is present, calculate the adjusted price with the 5G option price
        adjusted_price = newprice + offer['option5g']['price']
        extracted_data.append([data_envelope, True, adjusted_price])
    else:
        extracted_data.append([data_envelope, False, newprice])

    # Add a second entry with 5G set to False only if the 5G option was originally true
    if option5g_present:
        # For the second entry, use the original newprice without the 5G price addition
        extracted_data.append([data_envelope, False, newprice])

# Print the extracted data to verify the output
for data in extracted_data:
    print(data)


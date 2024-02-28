# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 12:51:10 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.reglomobile.fr/api/referentiel/Offers'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Convert the response to JSON format
    data = response.json()
else:
    print(f"Failed to retrieve data, status code: {response.status_code}")

new_data = []
for item in data:
    new_data.append(item['parametres']['titre'].split(' '))
    
extracted_data_updated = []  # Initializing a new list to store the updated format

for row in new_data:
    # Identify where the data volume is located based on the structure of each list
    if row[5] == 'Internet':
        data_volume = f"{row[6]}Go"
    else:
        data_volume = f"{row[4]}Go"
    # Extracting the technology type (True for 5G, False for 4G+), price correctly formatted
    technology_type = True if row[1] == '5G' else False
    price = row[2].replace(",", ".")
    extracted_data_updated.append((data_volume, technology_type, price))

# Now extracted_data_updated contains the desired format



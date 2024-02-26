# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 20:30:46 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re

response = requests.get('https://www.nrjmobile.fr/fr/forfait-mobile.html')

# Ensure BeautifulSoup is used with the response content, specifying 'lxml' as the parser
soup = BeautifulSoup(response.text, 'lxml')  # Use response.text to get the HTML content

# Find all <a> tags
a_tags = soup.find_all('a')

# Initialize a list to hold all onclick attributes
onclick_attributes = []

# Iterate over all found <a> tags to extract 'onclick' attributes
for a_tag in a_tags:
    onclick = a_tag.get('onclick')
    if onclick:  # Check if the onclick attribute exists
        onclick_attributes.append(onclick)

# Loop through each function call
extracted_data = []

for call in onclick_attributes:
    if "add_to_cart_click_product" in call:
        parts = call.split("'")
        forfait_name = parts[3]
        initial_price = parts[-1].split(",")[1]
        
        pattern_5g = re.compile(r"5g", re.IGNORECASE) # Added IGNORECASE for case-insensitive search        
        # Check if "5G" is present in the string
        extracted_5g = bool(pattern_5g.findall(forfait_name))
        # Use regular expression to find patterns of digits followed by 'go' or 'mo'
        data_volume_matches = re.findall(r'\d+\s*go|\d+\s*mo', forfait_name, re.IGNORECASE)

        if data_volume_matches:
            data_volume = data_volume_matches[0].replace("go", "Go").replace("mo", "Mo").replace(" ", "")
            # Format the price by ensuring the "€" symbol is at the front
            price_formatted = initial_price
            extracted_data.append((data_volume, extracted_5g, price_formatted))

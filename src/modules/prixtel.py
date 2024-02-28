# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:08:58 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re

response = requests.get('https://www.prixtel.com/')

# Ensure BeautifulSoup is used with the response content, specifying 'lxml' as the parser
soup = BeautifulSoup(response.text, 'lxml')  # Use response.text to get the HTML content

# Find all <li> elements with class 'wpx_prod'
wpx_prod_elements = soup.find_all("li", class_="wpx_prod")

# Initialize a list to hold the extracted URLs
urls = []

# Loop through each found element to extract the URL from the <a> tag
for element in wpx_prod_elements:
    a_tag = element.find("a")  # Find the <a> tag within the current <li> element
    if a_tag and a_tag.has_attr("href"):  # Check if the <a> tag exists and has an 'href' attribute
        urls.append('https://www.prixtel.com' + a_tag['href'])  # Add the URL to the list


extracted_name = []
extracted_price = []
extracted_network = []
# Print or process the extracted URLs
# Assuming 'urls' is your list of URLs
for new_url in urls:
    new_response = requests.get(new_url)
    new_soup = BeautifulSoup(new_response.text, 'lxml')  # Use response.text to get the HTML content
    
    # Extracting names
    names = new_soup.find_all(class_="box")[1:]
    alt_names = [plan.text for plan in names if plan.text]  
    extracted_name.append(alt_names)
    
    # Extracting prices
    prices = new_soup.find_all(class_="col2 off-promo")
    for price_group in prices:
        cleaned_str = price_group.text.replace('€', '').replace(' ', '').replace(',','.').split("/mois") # Remove '€' and '/mois'
        extracted_price.append(cleaned_str)
    
    #is5g    
    text_5g = new_soup.find_all(class_="header_content")
    pattern_5g = re.compile(r"5G")
    extracted_5g = [bool(pattern_5g.search(text.text)) for text in text_5g]
    extracted_network.append(extracted_5g)
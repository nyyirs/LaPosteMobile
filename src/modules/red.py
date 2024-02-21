# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:08:56 2024

@author: Nyyir
"""
import requests
from bs4 import BeautifulSoup
import json

# URL of the page to fetch
url = 'https://www.red-by-sfr.fr/forfaits-mobiles/'

# Make the HTTP request to get the webpage content
response = requests.get(url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.content, 'html.parser')

# Find the <amp-state> tag with the specific ID 'serviceOffer'
amp_state_tag = soup.find('amp-state', id='serviceOffer')

# Extract the JSON string from the <script> tag within <amp-state> if present
json_str = amp_state_tag.script.string if amp_state_tag and amp_state_tag.script else '{}'

# Parse the JSON string into a Python dictionary
data = json.loads(json_str)

datanat_codes_labels = [(entry["code"], entry["label"]) for entry in data["data"]["redOneOfferConfiguration"]["datanat"]]


# Base URL without query parameters
base_url = 'https://api.red-by-sfr.fr/service-offer-red/api/rest/v1/mobile'

# Networks to iterate over
networks = ['defaultNetwork', 'net5G']

# Placeholder for the results
results = []

# Loop through each code-label pair and network type
for code, label in datanat_codes_labels:
    for network in networks:
        # Construct the URL with the current code and network
        url = f'{base_url}?cNat={code}&cNet={network}&cInt=defaultDataInter'
        
        # Perform the GET request
        response = requests.get(url)
        
        if response.status_code == 200:
            # Parse the JSON response if the request was successful
            data = response.json()
            results.append((code, label, network, data["data"]["redOneOfferConfiguration"]["pricePerMonthWithDiscount"]))
        else:
            print(f"Failed to retrieve data for {code} ({label}) on {network}. Status code: {response.status_code}")

# At this point, 'results' contains the data from each successful request


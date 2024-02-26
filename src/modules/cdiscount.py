# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 21:28:32 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
# }

# response = requests.get('https://www.cdiscount.com/cdiscount-mobile/forfaits-mobile-sans-engagement/v-16401-16401.html', headers=headers)

# # Ensure BeautifulSoup is used with the response content, specifying 'lxml' as the parser
# soup = BeautifulSoup(response.text, 'lxml')  # Use response.text to get the HTML content

# names = soup.find_all(class_="mobileBdxTitre")
# alt_names = [plan.text.strip() for plan in names if plan.text.strip()]

import requests
import json

# The URL for the POST request - adjust this as needed
url = "https://115a4b14229tz55.lyfnh.io/dkp9lmi2eyts8"

# Example headers - these might need to include more specific entries like User-Agent, Content-Type, etc.
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Your User Agent Here"
}

# The payload based on the provided structure, adjust values as necessary
payload = {
    "sid": "TyxUPO5k9GxipSg7-C7qz",
    "cookieChecker": {
        "consentState": "",
        "cookies": [],
        "sessionStorage": [],
        "localStorage": []
    },
    "domObserver": {
        "changes": []
    },
    "domainDiscovery": {
        "hits": [
            {"name": "tr6.snapchat.com", "count": 1},
            {"name": "prebid-eu.creativecdn.com", "count": 1}
        ]
    },
    "linkWatcher": {
        "changes": [
            {"sanitized": True, "url": "https://www.dwin1.com/19624.js"}
        ]
    },
    "metadata": {
        "clientId": "T9lotqYiXv",
        "configVersion": "0.6.37",
        "pagetype": "Vitrine",
        "referrer": "https://www.cdiscount.com/cdiscount-mobile/v-164-0.html",
        "swVersion": "1.13.5",
        "tagVersion": "1.13.5",
        "tenantId": "wOWnAutKvL",
        "url": "https://www.cdiscount.com/cdiscount-mobile/forfaits-mobile-sans-engagement/v-16401-16401.html"
    },
    "methodOverride": {
        "hits": []
    }
}

# Convert the payload to JSON
data = json.dumps(payload)

# Sending the POST request
response = requests.post(url, headers=headers, data=data)

# Check the response
print("Status Code:", response.status_code)
print("Response Text:", response.text)

get_url = 'https://www.cdiscount.com/'
headers_get = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

response = requests.get(get_url, headers=headers_get)

# Ensure BeautifulSoup is used with the response content, specifying 'lxml' as the parser
soup = BeautifulSoup(response.text, 'lxml')  # Use response.text to get the HTML content

names = soup.find_all(class_="flow--xs")
alt_names = [plan.text.strip() for plan in names if plan.text.strip()]

# Output the results
print(alt_names)
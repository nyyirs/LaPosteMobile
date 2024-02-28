# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 12:37:36 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re

response = requests.get('https://www.coriolis.com/forfaits-sans-mobile')

# Ensure BeautifulSoup is used with the response content, specifying 'lxml' as the parser
soup = BeautifulSoup(response.text, 'lxml')  # Use response.text to get the HTML content

names = soup.find_all(class_="data")
alt_names = [plan.text.strip() for plan in names if plan.text.strip()]

# Find all divs with class 'network' and check for a child span with class 'five-g'
network_divs = soup.find_all(class_="offer-label-network-grid")
network_5g_presence = [bool(div.find("span", class_="five-g")) for div in network_divs]


prices = soup.find_all(class_="pricing")
alt_prices = [item.text.replace('€','.').replace('par mois', '').strip() for item in prices if item]
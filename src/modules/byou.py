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

#[Catalogue] => Contains other forfaits
#[offers] => main forfaits
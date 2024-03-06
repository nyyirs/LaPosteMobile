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




url = 'https://boutique.orange.fr/mobile/offres?_ga=2.146702900.1206541786.1707377648-761195977.1706858949&withOpenPrices=false'
response = requests.get(url)
if response.status_code != 200:
    logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
    raise Exception(f"Failed to fetch data from {url}")
soup = BeautifulSoup(response.content, 'html.parser')
logging.info("Successfully scraped data from Orange.")

"""Process scraped plan data."""
logging.info("Processing scraped data for Orange.")
plans = []
names = soup.find_all(class_="offer-tile")
alt_names = [item.text for item in names if item]
filtered_plan_names = [plan for plan in alt_names if " false " in plan and "24 mois " in plan]        

def extract_plan_info_with_duration_marker(plans):
    extracted_info = []

    for plan in filtered_plan_names:
        # Data volume and technology extraction
        data_vol_tech = plan.split("Forfait ")[1].split(" ")[0:2]
        data_vol_tech_str = " ".join(data_vol_tech)

        # Price extraction with duration distinction
        if 'puis' in plan:
            # For plans with a different price after 6 months
            price_6mo = plan.split('€ par mois pendant 6 mois puis')[0].split()[-1].replace(",", ".")
            price_after = plan.split('puis')[1].split('€')[0].strip().replace(",", ".")
            extracted_info.append([data_vol_tech_str, '5G', price_6mo, 1])  # 1 for the first 6 months
            extracted_info.append([data_vol_tech_str, '5G', price_after, 2])  # 2 for after 6 months
        else:
            # Single price throughout
            price = plan.split('€ par mois')[0].split()[-1].replace(",", ".")
            extracted_info.append([data_vol_tech_str, '5G', price, 2])  # Assuming 2 for 24 months duration for single price

    return extracted_info

# Apply the modified logic to include duration markers
final_list_with_duration_marker = extract_plan_info_with_duration_marker(alt_names)
final_list_with_duration_marker



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
import sys
import os

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_scraper import BaseScraper

class Sfr(BaseScraper):
    def __init__(self):
        super().__init__("SFR")
        logging.info("Initialized SFR Scraper Avec Engagement.")

    def scrape_data(self):
        """Scrape plan data from SFR's website."""
        logging.info("Scraping data from SFR.")
        url = self.operator_data['URLAvecEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from SFR.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for SFR.")
        self.plans = []
        names = self.soup.find_all('li', class_="cinqg")
        # Corrected: Removed parentheses from item.text
        alt_names = [item.text.split('Client Box')[0] for item in names if '24' in item.text]         
        re_data_amount = r"\d{1,3}\sGo"
        re_technology = r"5G|4G"
        re_price = r"\d{1,3}(?:[.,]\d{2})?\s?€|\d{2},\d{2}€(?:\/mois)?"        
        self.extracted_details_dynamic = []        
        for plan in alt_names:
            data_amount_matches = re.findall(re_data_amount, plan)
            technology_matches = re.findall(re_technology, plan)
            price_matches = re.findall(re_price, plan)
            prices = [price.replace(" ", "").replace("€", "").replace(",", ".") for price in price_matches]        
            # Correcting the cents part for prices and dynamically determining the plan duration
            prices_corrected = []
            for price in prices:
                if "." not in price:
                    price += ".99"  # Assuming missing cents should be ".99"
                prices_corrected.append(price)        
            if data_amount_matches and technology_matches:
                data_amount = data_amount_matches[0]
                technology = technology_matches[0]        
                # Dynamically determine if the plan is for 6 or 24 months based on the presence of specific phrases
                # Assuming that the presence of "pendant 6 mois" indicates a 6-months special pricing
                if "pendant 6 mois" in plan:
                    # First price is for 6 months, subsequent for 24
                    self.extracted_details_dynamic.append({'name': data_amount, 'is_5g': technology, 'price': prices_corrected[0], 'annee': 0.5})  # 6 months
                    for price in prices_corrected[1:]:
                        self.extracted_details_dynamic.append({'name': data_amount, 'is_5g': technology, 'price': prices[1], 'annee': 2})  # 24 months
                else:
                    # If no specific mention, assume all prices are for 24 months
                    for price_new in prices_corrected:
                        self.extracted_details_dynamic.append({'name': data_amount, 'is_5g': technology, 'price': price_new, 'annee': 2})  # 24 months

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for SFR.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.extracted_details_dynamic:
            limite, unite = re.match(r'([\d\sH]+)\s*(Go|Mo)', plan['name'].replace(' ', '')).groups()
            # Check if plan['is_5g'] is equal to '5G' and set the result to a boolean
            is_5g_compatible = True if plan['is_5g'] == '5G' else False            
            # Set compatible5g to 1 if is_5g_compatible is True, else set to 0
            compatible5g = 1 if is_5g_compatible else 0
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g, 0, 0, 1, plan['annee'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {compatible5g} with engagement 1 with annee {plan['annee']}")
        logging.info("Data insertion for SFR completed.")

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#     scraper = Sfr()
#     scraper.run()              

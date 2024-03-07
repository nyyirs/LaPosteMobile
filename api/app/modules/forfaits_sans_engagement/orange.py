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

class Orange(BaseScraper):
    def __init__(self):
        super().__init__("Orange")
        logging.info("Initialized Orange Scraper Sans Engagement.")

    def scrape_data(self):
        """Scrape plan data from Orange's website."""
        logging.info("Scraping data from Orange.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from Orange.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Orange.")
        self.plans = []
        names = self.soup.find_all(class_="offer-tile")
        alt_names = [item.text for item in names if item]
        filtered_plan_names = [plan for plan in alt_names if " false " in plan]        
        pattern = re.compile(r"Forfait \d+h \d+Go|Forfait \d+Go 5G|Forfait \d+h \d+Mo|Forfait \d+Mo|Forfait \d+Go|Série Spéciale \d+Go 5G")
        extracted_texts = [re.search(pattern, plan).group(0) if re.search(pattern, plan) else None for plan in filtered_plan_names]        
        pattern = r'^.*?(\d)'
        modified_texts = [re.sub(pattern, r'\1', text) for text in extracted_texts]        
        # Extract the 5G
        pattern_5g = re.compile(r"5G")
        extracted_5g = [bool(pattern_5g.search(text)) for text in modified_texts if text.strip()]        
        # Extract the price
        extracted_prices = []
        for plan in filtered_plan_names:
            match = re.search(r'(\d+,\d+)€', plan)
            if match:
                price = match.group(1).replace(",", ".")
                extracted_prices.append(f"{price}")
        for name, is_5g, price in zip(modified_texts[2:], extracted_5g[2:], extracted_prices[2:]):
            self.plans.append({'name': name, 'is_5g': is_5g, 'price': price})        
        logging.info(f"Processed {len(self.plans)} plans for Orange.")

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Orange.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            match = re.match(r'((?:\d+h)?\s*\d+)\s*(Go|Mo)', plan['name'].strip())
            if match:
                limite = match.group(1).strip().replace(' ', '')  # Extract and strip to remove leading/trailing spaces
                unite = match.group(2).strip()
            compatible5g = 1 if plan['is_5g'] else 0
            price = plan['price']
            if plan['is_5g']:
                forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g, 0, 0, 0, 'NULL')
                self.db_operations.insert_into_tarifs(forfait_id, price, date_enregistrement)
                logging.info(f"Inserted plan {plan['name']} with price {price} with is5G {plan['is_5g']}")                
            else:
                forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, 0, 0, 0, 0, 'NULL')
                self.db_operations.insert_into_tarifs(forfait_id, price, date_enregistrement)
                logging.info(f"Inserted plan {plan['name']} with price {price} with is5G {plan['is_5g']}")
        logging.info("Data insertion for Orange completed.")

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#     scraper = Orange()
#     scraper.run()         
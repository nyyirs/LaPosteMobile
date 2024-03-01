# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 14:51:25 2024

@author: nyyir.m.soobrattee
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
import datetime
from modules.base_scraper import BaseScraper
import re

class Byou(BaseScraper):
    def __init__(self):
        super().__init__("B&You")
        logging.info("Initialized B&You Scraper.")

    def scrape_data(self):
        """Scrape plan data from B&You's website."""
        logging.info("Scraping data from B&You.")
        url = self.operator_data['URLSansEngagement']
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.text, 'html.parser')
        logging.info("Successfully scraped data from B&You.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for B&You.")
        script_tag = self.soup.find('script', id='__NEXT_DATA__')
        json_str = script_tag.string if script_tag else '{}'
        data = json.loads(json_str)
        
        self.plans = self._extract_plans(data)
        
        logging.info(f"Processed {len(self.plans)} plans for Orange.")

    def _extract_plans(self, data):
        """Extract plans from JSON data."""
        
        main_offers = data['props']['pageProps']['productsList']['offers']        
        plans = []
        
        for offer in main_offers:
            data_envelope = offer['data_envelope']
            newprice = offer['newprice']
            option5g_present = bool(offer.get('option5g'))
        
            if option5g_present:
                adjusted_price = newprice + offer['option5g']['price']
                plans.append((data_envelope, True, adjusted_price))
            else:
                plans.append((data_envelope, True, newprice))
            
            if option5g_present:
                plans.append((data_envelope, False, newprice))
        return plans

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for B&You.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for name, is_5g, price in self.plans:
            # Assuming 'name' format needs parsing for 'limite' and 'unite'
            match = re.match(r'((?:\d+h)?\s*\d+)\s*(Go|Mo)', name)
            limite, unite = match.groups() if match else (None, None)
            compatible5g = 1 if is_5g else 0
            
            if is_5g:
                forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
                self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, price, date_enregistrement)
                logging.info(f"Inserted plan {name} with price {price} with {is_5g}")
            else:
                forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, 0)
                self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, price, date_enregistrement)
                logging.info(f"Inserted plan {name} with price {price} with {is_5g}")
                
        logging.info("Data insertion for B&You completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Byou()
    scraper.run()
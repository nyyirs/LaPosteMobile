# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 21:00:02 2024

@author: Nyyir
"""

import requests
import datetime
import logging
import sys
import os

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_scraper import BaseScraper

class sfr(BaseScraper):
    def __init__(self):
        super().__init__("SFR")
        logging.info("Initialized SFR Scraper Fixe.")

    def scrape_data(self):
        """Scrape plan data from SFR website."""
        logging.info("Scraping data from SFR.")
        url = self.operator_data['URLFixe']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.data = response.json()
        logging.info("Successfully scraped data from SFR.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data.")
        """Process scraped plan data."""
        logging.info("Processing scraped data.")
        self.plans = []
        for item in self.data['data']['offers']['FIXE_CONQUETE']['offers']:
            if ('sfr-fibre-starter' in item['seoName'] or 'sfr-fibre-power' in item['seoName'] or 'sfr-fibre-premium' in item['seoName']) and not item['seoName'].endswith(('-2p', '-tv')):                
                self.plans.append({'name': item['seoName'], 'annee': (item['plans'][0]['commitmentDuration'] / 12), 'price': item['plans'][0]['pricePerMonth'], 'adsl': 0, 'fibre': 1, 'is_5g': 0, 'avecEngagement': 0 })
            elif ('sfr-adsl-starter' in item['seoName'] or 'sfr-adsl-power' in item['seoName'] or 'sfr-adsl-premium' in item['seoName']) and not item['seoName'].endswith(('-2p', '-tv')):                
                self.plans.append({'name': item['seoName'], 'annee': (item['plans'][0]['commitmentDuration'] / 12), 'price': item['plans'][0]['pricePerMonth'], 'adsl': 1, 'fibre': 0, 'is_5g': 0, 'avecEngagement': 0 })                
        for plan in self.plans:
            plan['price'] = '{:.2f}'.format(plan['price'] / 100)

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for SFR.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], plan['name'], 'NULL', plan['is_5g'], plan['adsl'], plan['fibre'], plan['avecEngagement'], plan['annee'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']}")
        logging.info("Data insertion for SFR completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = sfr()
    scraper.run()                


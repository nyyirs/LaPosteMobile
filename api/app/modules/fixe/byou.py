# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 13:15:50 2024

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

class byou(BaseScraper):
    def __init__(self):
        super().__init__("B&You")
        logging.info("Initialized B&You Scraper Fixe.")

    def scrape_data(self):
        """Scrape plan data from B&You website."""
        logging.info("Scraping data from B&You.")
        url = self.operator_data['URLFixe']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.data = response.json()
        logging.info("Successfully scraped data from B&You.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data.")
        """Process scraped plan data."""
        logging.info("Processing scraped data.")
        self.plans = []
        for item in self.data:
            if 'promotion' in item['product']:  # Check if 'promotion' key exists in 'product'
                # Calculate the corrected 'annee' and 'price' based on the promotion
                mois = item['product']['promotion']['duration'] / 12
                mois_price = float(item['product']['price']) - float(item['product']['promotion']['amount'])
                annee = int(item['product']['obligation'].replace('monthly', '')) / 12
                annee_price = item['product']['price']                
                # Append a new dictionary to the 'plans' list with the corrected structure
                self.plans.append({
                    'name': item['title'],  # Assuming 'title' is directly under 'item'
                    'annee': mois,
                    'price': mois_price,
                    'adsl': 0,
                    'fibre': 1,
                    'is_5g': 0,
                    'avecEngagement': 0
                })                
                self.plans.append({
                    'name': item['title'],  # Assuming 'title' is directly under 'item'
                    'annee': annee,
                    'price': annee_price,
                    'adsl': 0,
                    'fibre': 1,
                    'is_5g': 0,
                    'avecEngagement': 0
                })                 
            elif ('obligation' in item['product']):
                if 'Série Spéciale Bbox' in item['title']: 
                    annee = int(item['product']['obligation'].replace('monthly', '')) / 12
                    annee_price = item['product']['price']
                    self.plans.append({
                        'name': item['title'],  # Assuming 'title' is directly under 'item'
                        'annee': annee,
                        'price': annee_price,
                        'adsl': 0,
                        'fibre': 1,
                        'is_5g': 0,
                        'avecEngagement': 0
                    })                 
        for plan in self.plans:
            plan['price'] = '{:.2f}'.format(float(plan['price'])) 
        self.plans = list({(plan['name'], plan['price']): plan for plan in reversed(self.plans)}.values())

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], plan['name'], 'NULL', plan['is_5g'], plan['adsl'], plan['fibre'], plan['avecEngagement'], plan['annee'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']}")
        logging.info("Data insertion for B&You completed.")        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = byou()
    scraper.run()     
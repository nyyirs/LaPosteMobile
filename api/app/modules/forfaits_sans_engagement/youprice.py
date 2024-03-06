# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 16:47:04 2024

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

class Youprice(BaseScraper):
    def __init__(self):
        super().__init__("Youprice")
        logging.info("Initialized Youprice Scraper.")

    def scrape_data(self):
        """Scrape plan data from Youprice's website."""
        logging.info("Scraping data from Youprice.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.data = response.json()
        logging.info("Successfully scraped data from Youprice.")
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Youprice.")
        self.plans = []
        for item in self.data:
            for tarif in item['tarifs']:
                # Extracting the required information
                volume_max = tarif['volumeMax']
                price = tarif['tarif']
                is_5g_authorized = item['is5GAuthorized']                
                # Extracting the specific part of the description
                description_part = item['description'].split(' ')[-1]              
                # Concatenating description with volumeMax
                description_concat = f"{volume_max}{description_part}"                
                self.plans.append({'name': description_concat, 'is_5g': is_5g_authorized, 'price': price})
        logging.info(f"Processed {len(self.plans)} plans for Youprice.")          

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Youprice.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g, 0, 'NULL')
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")
        logging.info("Data insertion for Youprice completed.")  

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Youprice()
    scraper.run()
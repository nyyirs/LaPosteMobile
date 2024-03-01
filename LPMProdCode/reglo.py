# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 12:51:10 2024

@author: Nyyir
"""
import requests
import datetime
import logging
from base_scraper import BaseScraper

class Reglo(BaseScraper):
    def __init__(self):
        super().__init__("Reglo Mobile")
        logging.info("Initialized Reglo Mobile Scraper.")

    def scrape_data(self):
        """Scrape plan data from Reglo Mobile's website."""
        logging.info("Scraping data from Reglo Mobile.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.data = response.json()    
        logging.info("Successfully scraped data from Reglo Mobile.")
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Reglo Mobile.")
        self.plans = []
        
        new_data = []
        for item in self.data:
            new_data.append(item['parametres']['titre'].split(' '))
        
        for row in new_data:
            # Identify where the data volume is located based on the structure of each list
            if row[5] == 'Internet':
                data_volume = f"{row[6]}Go"
            else:
                data_volume = f"{row[4]}Go"
            # Extracting the technology type (True for 5G, False for 4G+), price correctly formatted
            technology_type = True if row[1] == '5G' else False
            price = row[2].replace(",", ".")
            self.plans.append({'name': data_volume, 'is_5g': technology_type, 'price': price})  
        
    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Reglo Mobile.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0

            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")

        logging.info("Data insertion for Reglo Mobile completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Reglo()
    scraper.run()      
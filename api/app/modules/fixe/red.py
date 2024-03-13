# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 09:58:35 2024

@author: Nyyir
"""

import requests
import datetime
from bs4 import BeautifulSoup
import logging
import sys
import os

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_scraper import BaseScraper

class red(BaseScraper):
    def __init__(self):
        super().__init__("RED")
        logging.info("Initialized RED Scraper Fixe.")

    def scrape_data(self):
        """Scrape plan data from RED website."""
        logging.info("Scraping data from RED.")
        url = self.operator_data['URLFixe']  # Adjust based on actual key name
        url_fibre = requests.get(url.split(';')[0])
        url_adsl = requests.get(url.split(';')[1])
        if url_fibre.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {url_fibre.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        if url_adsl.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {url_adsl.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")        
        self.soup_fibre = BeautifulSoup(url_fibre.content, 'html.parser')
        self.soup_adsl = BeautifulSoup(url_adsl.content, 'html.parser')
        logging.info("Successfully scraped data from RED.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data.")
        self.plans = []
        name_content_fibre = self.soup_fibre.find('div', id='bandeau')
        name_content_adsl = self.soup_adsl.find('div', id='bandeau')
        price_content_fibre = self.soup_fibre.find('div', class_='priceComponent')
        price_content_adsl = self.soup_adsl.find('div', class_='priceComponent')
        alt_names_content_fibre = [item.text.strip().split('sans')[0] for item in name_content_fibre if item.text.strip()]
        alt_names_content_adsl = [item.text.strip().split('sans')[0]  for item in name_content_adsl if item.text.strip()]
        alt_price_content_fibre = [item.text.strip() for item in price_content_fibre if item.text.strip()][0].replace(',', '.')
        alt_price_content_adsl = [item.text.strip() for item in price_content_adsl if item.text.strip()][0].replace(',', '.')
        for index, item_fibre in enumerate(alt_names_content_fibre):
            self.plans.append({'name': item_fibre, 'annee': 2, 'price': alt_price_content_fibre, 'adsl': 0, 'fibre': 1, 'is_5g': 0, 'avecEngagement': 0 })
            
        for index, item_adsl in enumerate(alt_names_content_adsl):
            self.plans.append({'name': item_adsl, 'annee': 2, 'price': alt_price_content_adsl, 'adsl': 1, 'fibre': 0, 'is_5g': 0, 'avecEngagement': 0 })

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for RED.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], plan['name'], 'NULL', plan['is_5g'], plan['adsl'], plan['fibre'], plan['avecEngagement'], plan['annee'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']}")
        logging.info("Data insertion for RED completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = red()
    scraper.run()                    
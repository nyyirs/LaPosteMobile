# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 12:37:36 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import datetime
import logging
from base_scraper import BaseScraper

class Coriolis(BaseScraper):
    def __init__(self):
        super().__init__("Coriolis télécom")
        logging.info("Initialized Coriolis télécom Scraper.")

    def scrape_data(self):
        """Scrape plan data from Coriolis télécom's website."""
        logging.info("Scraping data from Coriolis télécom.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from Coriolis télécom.")
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Coriolis télécom.")
        self.plans = []

        names = self.soup.find_all(class_="data")
        alt_names = [plan.text.strip() for plan in names if plan.text.strip()]
        
        # Find all divs with class 'network' and check for a child span with class 'five-g'
        network_divs = self.soup.find_all(class_="offer-label-network-grid")
        network_5g_presence = [bool(div.find("span", class_="five-g")) for div in network_divs]
        
        
        prices = self.soup.find_all(class_="pricing")
        alt_prices = [item.text.replace('€','.').replace('par mois', '').strip() for item in prices if item]
        
        for name, is5g, price in zip(alt_names, network_5g_presence, alt_prices):
            self.plans.append({'name': name, 'is_5g': is5g, 'price': price})  
            
    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Coriolis télécom.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0

            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")

        logging.info("Data insertion for Coriolis télécom completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Coriolis()
    scraper.run()                
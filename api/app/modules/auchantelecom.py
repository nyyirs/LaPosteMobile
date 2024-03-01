# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 21:00:46 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import datetime
import logging
import re
from modules.base_scraper import BaseScraper
from collections import OrderedDict

class Auchan(BaseScraper):
    def __init__(self):
        super().__init__("Auchan Telecom")
        logging.info("Initialized Auchan Telecom Scraper.")

    def scrape_data(self):
        """Scrape plan data from Auchan Telecom's website."""
        logging.info("Scraping data from Auchan Telecom.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from Auchan Telecom.")
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Auchan Telecom.")
        
        self.plans = []  
        
        names = self.soup.find_all(class_="data")
        alt_names = [plan.text.strip() for plan in names if 'Internet' not in plan.text.strip()]
        extracted_texts = list(OrderedDict.fromkeys(alt_names))
        
        alt_5g = [plan.text.strip() for plan in names if plan.text.strip()]
        filtered_5g = [name for name in alt_5g if len(name) > 10]
        pattern_5g = re.compile(r"5g")
        extracted_5g = [bool(pattern_5g.search(text)) for text in filtered_5g if text.strip()]
        
        prices = self.soup.find_all(class_="price")
        prices = [item.text.strip() for item in prices if item]
        prices_no_duplicates = list(OrderedDict.fromkeys(prices))
        prices = [price.replace("€", ".").replace("/mois", "") for price in prices_no_duplicates if '€' in price]
        
        for name, is5g, price in zip(extracted_texts, extracted_5g, prices):
            self.plans.append({'name': name, 'is_5g': is5g, 'price': price})
            
    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Auchan Telecom.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0

            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")

        logging.info("Data insertion for Auchan Telecom completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Auchan()
    scraper.run()               
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 08:58:40 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
import logging
from modules.base_scraper import BaseScraper

class Sosh(BaseScraper):
    def __init__(self):
        super().__init__("Sosh")
        logging.info("Initialized Sosh Scraper.")

    def scrape_data(self):
        """Scrape plan data from Sosh's website."""
        logging.info("Scraping data from Sosh.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from Sosh.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Sosh.")
        self.plans = []

        names = self.soup.find_all(class_="title")
        alt_names = [plan.text for plan in names if "Bloqués" not in plan.text]

        prices = self.soup.find_all(class_="price-amount")
        alt_prices = [price.text.strip().replace("€", "").replace(",", ".") for price in prices]

        pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
        extracted_texts = [pattern.search(text).group(0) for text in alt_names if pattern.search(text)]
        
        extracted_5g = [bool(re.search(r"5G", text)) for text in alt_names]

        for name, is_5g, price in zip(extracted_texts, extracted_5g, alt_prices):
            self.plans.append({'name': name, 'is_5g': is_5g, 'price': price})
        
        logging.info(f"Processed {len(self.plans)} plans for Sosh.")

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Sosh.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0

            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")

        logging.info("Data insertion for Sosh completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Sosh()
    scraper.run()
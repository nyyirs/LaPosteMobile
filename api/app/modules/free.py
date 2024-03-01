# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 09:43:56 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
import logging
from modules.base_scraper import BaseScraper
from collections import OrderedDict

class Free(BaseScraper):
    def __init__(self):
        super().__init__("Free")
        logging.info("Initialized Free Scraper.")

    def scrape_data(self):
        """Scrape plan data from Free's website."""
        logging.info("Scraping data from Free.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from Free.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Free.")
        self.plans = []

        names = self.soup.find_all(class_="ml-4 text-14")
        alt_names = [item.text for item in names if item]
        
        pattern = r"Internet\s(\d+)\s(Mo|Go)\sen\s([45]G\+?\/[45]G\+?)"
        extracted_names = list(set([match for text in alt_names for match in re.findall(pattern, text) if match]))
        extracted_names.sort(key=lambda x: int(x[0]), reverse=True)
        extracted_names = list(OrderedDict.fromkeys(extracted_names))

        prices = self.soup.find_all(class_="h-[min-content]")
        alt_prices = [item.text for item in prices if item][:len(extracted_names)]

        prices_decimal = self.soup.find_all(class_="ml-1 self-start")
        alt_prices_decimal = [f".{item.text.replace('/mois','').replace('€','')}" if item.text.replace('/mois','').replace('€','').strip() else '' for item in prices_decimal if item][:len(extracted_names)]

        for name, price, price_decimal in zip(extracted_names, alt_prices, alt_prices_decimal):
            is_5g = '5G' in name[2]
            formatted_price = f"{price}{price_decimal}"
            self.plans.append({'name': f"{name[0]}{name[1]}", 'is_5g': is_5g, 'price': formatted_price})
        
        logging.info(f"Processed {len(self.plans)} plans for Free.")

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Free.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0

            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")

        logging.info("Data insertion for Free completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Free()
    scraper.run()
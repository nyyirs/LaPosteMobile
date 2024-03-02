# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 08:51:34 2024

@author: Nyyir
"""

import requests
import re
from bs4 import BeautifulSoup
import datetime
import logging
from modules.base_scraper import BaseScraper

class Syma(BaseScraper):
    def __init__(self):
        super().__init__("Syma")
        logging.info("Initialized Syma Scraper.")

    def scrape_data(self):
        """Scrape plan data from Syma's website."""
        logging.info("Scraping data from Syma.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from Syma.")
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Syma.")
        self.plans = []
        names = self.soup.find_all("span", class_="red")
        # Use a list comprehension with a condition to preserve order and remove duplicates
        alt_names = []
        [alt_names.append(plan.text.strip().replace(' ', '')) for plan in names if plan.text.strip() and plan.text.strip().replace(' ', '') not in alt_names]        
        prices = self.soup.find_all("div", class_="forfaits_top_list_item")
        alt_prices = [price.text.strip().replace('\n',' ') for price in prices if price.text.strip()]        
        network_technology = [True if '5G' in text else False if '4G' in text else None for text in alt_prices][:4]        
        # Extract the price and replace ' €' with '.'
        prices_only = [re.search(r'(\d+)\s€(\d+)', text) for text in alt_prices]
        prices_formatted = [f"{match.group(1)}.{match.group(2)}" for match in prices_only if match]
        for name, is5g, price in zip(alt_names, network_technology, prices_formatted):
            self.plans.append({'name': name, 'is_5g': is5g, 'price': price})
        logging.info(f"Processed {len(self.plans)} plans for Syma.")

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Syma.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")
        logging.info("Data insertion for Syma completed.")           
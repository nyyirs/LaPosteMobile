# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 11:35:12 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
import logging
from base_scraper import BaseScraper

class Sfr(BaseScraper):
    def __init__(self):
        super().__init__("SFR")
        logging.info("Initialized SFR Scraper.")

    def scrape_data(self):
        """Scrape plan data from SFR's website."""
        logging.info("Scraping data from SFR.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from SFR.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for SFR.")
        self.plans = []

        names = self.soup.find_all(class_="title")
        alt_names = [item.text for item in names if item]
        
        pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
        extracted_texts = [item for item in alt_names if pattern.search(item)]
        
        pattern_5g = re.compile(r"5G")
        extracted_5g = [bool(pattern_5g.search(text)) for text in extracted_texts if text.strip()]
        
        prix_entier = self.soup.find_all(class_="L")
        prix_decimal = self.soup.find_all(class_="R")
        alt_prices = [item.text.strip() for item in prix_entier if item]
        alt_decimals = [item.text.strip() for item in prix_decimal if item]
        cleaned_list_decimals = [item for item in alt_decimals if item != '/mois']
        
        plan_prices = []
        for text, price, decimal in zip(extracted_texts, alt_prices, cleaned_list_decimals):
            if not decimal:
                decimal_part = ''
            else:
                match = re.search(r"(\d+)", decimal)
                decimal_part = match.group(1) if match else ''
            full_price = f"{price}" + (f".{decimal_part}" if decimal_part else "")
            plan_prices.append(full_price)
            
        for name, is_5g, price in zip(extracted_texts[2:], extracted_5g[2:], plan_prices[2:]):
            self.plans.append({'name': name, 'is_5g': is_5g, 'price': price})   

        logging.info(f"Processed {len(self.plans)} plans for SFR.")

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for SFR.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = re.match(r'([\d\sH]+)\s*(Go|Mo)', plan['name'].replace(' ', '')).groups()
            compatible5g = 1 if plan['is_5g'] else 0
            price = plan['price']

            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, price, date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {price} with is5G {plan['is_5g']}.")

        logging.info("Data insertion for SFR completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Sfr()
    scraper.run()
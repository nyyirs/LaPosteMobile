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
import sys
import os

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_scraper import BaseScraper

class Lapostemobile(BaseScraper):
    def __init__(self):
        super().__init__("La Poste Mobile")
        logging.info("Initialized La Poste Mobile Scraper.")

    def scrape_data(self):
        """Scrape plan data from La Poste Mobile's website."""
        logging.info("Scraping data from La Poste Mobile.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from La Poste Mobile.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data.")
        self.plans = []
        # Extract plan details
        names = self.soup.find_all(id="imgCaracteristique")
        prix_entier = self.soup.find_all(class_="prix_entier")
        prix_decimal = self.soup.find_all(class_="decimal")
        prix_5g = self.soup.find_all(class_="option5g")        
        alt_names = [name['alt'] for name in names if name]
        formatted_names = [text.replace('<br/>', '\n') for text in alt_names]
        pattern = re.compile(r"\b\d+(?:Go|Mo)\b")
        pattern_5g = re.compile(r"5G")
        extracted_names = [pattern.search(text).group(0) for text in formatted_names if pattern.search(text)]
        extracted_5g = [bool(pattern_5g.search(text)) for text in formatted_names if text.strip()]        
        alt_prices = [item.text.strip() for item in prix_entier if item]
        alt_decimals = [item.text.strip() for item in prix_decimal if item]
        alt_prices_5g = [item.text.strip() for item in prix_5g if item]        
        plan_prices = []
        for text, price, decimal in zip(extracted_names, alt_prices, alt_decimals):
            decimal_part = re.search(r"(\d+)", decimal).group(1) if decimal else ''
            full_price = f"€{price}" + (f".{decimal_part}" if decimal_part else "")
            plan_prices.append(full_price)        
        extracted_5g_Add = [int(''.join(filter(str.isdigit, item))) if any(c.isdigit() for c in item) else 0 for item in alt_prices_5g]
        if len(extracted_5g) > len(extracted_5g_Add):
            extracted_5g_Add.extend([0] * (len(extracted_5g) - len(extracted_5g_Add)))
        for name, is_5g, price, price_addon in zip(extracted_names, extracted_5g, plan_prices, extracted_5g_Add):
            self.plans.append({'name': name, 'is_5g': is_5g, 'price': price, 'price_addon': price_addon})
        logging.info(f"Processed {len(self.plans)} plans.")

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            # Dummy data parsing, replace with actual logic
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0
            price_float = float(plan['price'][1:])
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, 0, 0, 0, 0, 'NULL')
            self.db_operations.insert_into_tarifs(forfait_id, f"{price_float:.2f}", date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {price_float:.2f} with is5G {plan['is_5g']}")
            if plan['is_5g']:
                new_price_float = price_float + plan['price_addon']
                forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g, 0, 0, 0, 'NULL')
                self.db_operations.insert_into_tarifs(forfait_id, f"{new_price_float:.2f}", date_enregistrement)
                logging.info(f"Inserted plan {plan['name']} with price {new_price_float:.2f} with is5G {plan['is_5g']}")
        logging.info("Data insertion for La Poste Mobile completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Lapostemobile()
    scraper.run()             
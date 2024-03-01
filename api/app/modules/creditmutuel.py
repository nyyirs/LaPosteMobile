# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 11:33:45 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import datetime
import logging
import re
from modules.base_scraper import BaseScraper

class Creditmutuel(BaseScraper):
    def __init__(self):
        super().__init__("Crédit mutuel mobile")
        logging.info("Initialized Crédit mutuel mobile Scraper.")

    def scrape_data(self):
        """Scrape plan data from Crédit mutuel mobile's website."""
        logging.info("Scraping data from Crédit mutuel mobile.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from Crédit mutuel mobile.")
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Crédit mutuel mobile.")
        self.plans = []
        
        names = self.soup.find_all(class_="card__data")
        alt_names = [plan.text.strip() for plan in names if plan.text.strip()]
        
        is5g = self.soup.find_all(class_="card__speed")
        pattern_5g = re.compile(r"5G")
        extracted_5g = [bool(pattern_5g.search(text.text)) for text in is5g]
        
        price_big_elements = self.soup.find_all(class_="card__price__big")
        price_bis_elements = self.soup.find_all(class_="card__price__bis")
        # Assuming each 'card__price__big' is followed by a 'card__price__bis', we pair them
        full_prices = []
        for big, bis in zip(price_big_elements, price_bis_elements):
            big_text = big.get_text(strip=True)
            bis_text = bis.div.get_text(strip=True).replace(u'\xa0', u' ').replace("€", "").replace(",",".").replace(" ","")
            full_prices.append(big_text + bis_text)
        for name, is5g, price in zip(alt_names, extracted_5g, full_prices):
            self.plans.append({'name': name.replace(" ", ""), 'is_5g': is5g, 'price': price})
            
    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Crédit mutuel mobile.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0

            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")

        logging.info("Data insertion for Crédit mutuel mobile completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Creditmutuel()
    scraper.run()                
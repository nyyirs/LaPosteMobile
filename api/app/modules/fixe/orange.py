# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 08:59:32 2024

@author: Nyyir
"""

import requests
import datetime
from bs4 import BeautifulSoup
import logging
import sys
import os
import json

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_scraper import BaseScraper

class orange(BaseScraper):
    def __init__(self):
        super().__init__("Orange")
        logging.info("Initialized Orange Scraper Fixe.")

    def scrape_data(self):
        """Scrape plan data from Orange website."""
        logging.info("Scraping data from Orange.")
        url = self.operator_data['URLFixe']  # Adjust based on actual key name
        response_fibre = requests.get(url.split(';')[0])
        response_adsl = requests.get(url.split(';')[1])
        if response_fibre.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response_fibre.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        if response_adsl.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response_adsl.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")        
        self.soup_fibre = BeautifulSoup(response_fibre.content, 'html.parser')
        self.soup_adsl = BeautifulSoup(response_adsl.content, 'html.parser')
        logging.info("Successfully scraped data from Orange.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data.")
        self.plans = []
        # Find the div with the specified class
        div_content_fibre = self.soup_fibre.find('div', class_='site-width site-height mb-0')
        div_content_adsl = self.soup_adsl.find('div', class_='site-width site-height mb-0')
        # Extract the script content within the div
        script_content_fibre = div_content_fibre.script.string
        script_content_adsl = div_content_adsl.script.string
        # Find the start and end of the JSON object in the script
        start_fibre = script_content_fibre.find('{')
        end_fibre = script_content_fibre.rfind('};') + 1
        start_adsl = script_content_adsl.find('{')
        end_adsl = script_content_adsl.rfind('};') + 1
        # Extract the JSON string
        json_str_fibre = script_content_fibre[start_fibre:end_fibre]
        json_str_adsl = script_content_adsl[start_adsl:end_adsl]
        # Convert the string to a JSON object
        data_fibre = json.loads(json_str_fibre)
        data_adsl = json.loads(json_str_adsl)
        for offer_fibre in data_fibre['offers']:            
            if (offer_fibre['price']['duration'] == 0):        
                annee = int(offer_fibre['price']['priceDetails'].split(' ')[1]) / 12        
                self.plans.append({'name': offer_fibre['name'], 'annee': int(annee), 'price': offer_fibre['price']['initialPrice'], 'adsl': 0, 'fibre': 1, 'is_5g': 0, 'avecEngagement': 0 })                
            else:
                self.plans.append({'name': offer_fibre['name'], 'annee': int(offer_fibre['price']['duration']) / 12, 'price': offer_fibre['price']['price'], 'adsl': 0, 'fibre': 1, 'is_5g': 0, 'avecEngagement': 0})
                self.plans.append({'name': offer_fibre['name'], 'annee': int(int(offer_fibre['price']['priceDetails'].split(' ')[1]) / 12), 'price': offer_fibre['price']['initialPrice'], 'adsl': 0, 'fibre': 1, 'is_5g': 0, 'avecEngagement': 0 })                
        for offer_adsl in data_adsl['offers']:            
            if (offer_adsl['price']['duration'] == 0):        
                annee = int(offer_adsl['price']['priceDetails'].split(' ')[1]) / 12        
                self.plans.append({'name': offer_adsl['name'], 'annee': int(annee), 'price': offer_adsl['price']['initialPrice'], 'adsl': 1, 'fibre': 0, 'is_5g': 0, 'avecEngagement': 0 })                
            else:
                self.plans.append({'name': offer_adsl['name'], 'annee': int(offer_adsl['price']['duration']) / 12, 'price': offer_adsl['price']['price'], 'adsl': 1, 'fibre': 0, 'is_5g': 0, 'avecEngagement': 0})
                self.plans.append({'name': offer_adsl['name'], 'annee': int(int(offer_adsl['price']['priceDetails'].split(' ')[1]) / 12), 'price': offer_adsl['price']['initialPrice'], 'adsl': 1, 'fibre': 0, 'is_5g': 0, 'avecEngagement': 0 })
                
    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Orange.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], plan['name'], 'NULL', plan['is_5g'], plan['adsl'], plan['fibre'], plan['avecEngagement'], plan['annee'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']}")
        logging.info("Data insertion for Orange completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = orange()
    scraper.run()                     



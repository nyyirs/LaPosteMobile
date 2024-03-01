# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 20:30:46 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import datetime
import logging
import re
from base_scraper import BaseScraper

class Nrj(BaseScraper):
    def __init__(self):
        super().__init__("NRJ Mobile")
        logging.info("Initialized NRJ Scraper.")

    def scrape_data(self):
        """Scrape plan data from NRJ's website."""
        logging.info("Scraping data from NRJ.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from NRJ.")
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for NRJ.")
        self.plans = []        
        
        names = [img.find('img')['src'] for img in self.soup.find_all('div', class_='data_prix')]
        
        alt_names = []
        alt_prices = []
        
        for name in names:
            alt_names.append(name.split('/')[4].split('_')[0])
            alt_prices.append(name.split('/')[4].split('_')[1].replace('.svg','').replace('e','.'))
        
        # Find all <a> tags
        a_tags = self.soup.find_all('a')
        
        # Initialize a list to hold all onclick attributes
        onclick_attributes = []
        
        # Iterate over all found <a> tags to extract 'onclick' attributes
        for a_tag in a_tags:
            onclick = a_tag.get('onclick')
            if onclick:  # Check if the onclick attribute exists
                onclick_attributes.append(onclick)
        
        # Loop through each function call
        alt_5g = []
        for call in onclick_attributes:
            parts = call.split("'")
            if "add_to_cart_click_product" in call:   
                forfait_name = parts[3]
                pattern_5g = re.compile(r"5g", re.IGNORECASE) # Added IGNORECASE for case-insensitive search        
                extracted_5g = bool(pattern_5g.findall(forfait_name))
                alt_5g.append(extracted_5g)
                
        for name, is_5g, price in zip(alt_names, alt_5g, alt_prices):
            self.plans.append({'name': name, 'is_5g': is_5g, 'price': price})
        
        logging.info(f"Processed {len(self.plans)} plans for NRJ.")

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for NRJ.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0

            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")

        logging.info("Data insertion for NRJ completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Nrj()
    scraper.run()                 
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:08:56 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import json
import datetime
import logging
import sys
import os

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_scraper import BaseScraper

class Red(BaseScraper):
    def __init__(self):
        super().__init__("RED")
        logging.info("Initialized RED Scraper.")

    def scrape_data(self):
        """Scrape plan data from RED's website."""
        logging.info("Scraping data from RED.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from RED.")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for RED.")
        self.plans = []     
        # Find the <amp-state> tag with the specific ID 'serviceOffer'
        amp_state_tag = self.soup.find('amp-state', id='serviceOffer')        
        # Extract the JSON string from the <script> tag within <amp-state> if present
        json_str = amp_state_tag.script.string if amp_state_tag and amp_state_tag.script else '{}'        
        # Parse the JSON string into a Python dictionary
        data = json.loads(json_str)        
        datanat_codes_labels = [(entry["code"], entry["label"]) for entry in data["data"]["redOneOfferConfiguration"]["datanat"]] 
        # Base URL without query parameters
        base_url = 'https://api.red-by-sfr.fr/service-offer-red/api/rest/v1/mobile'
        # Networks to iterate over
        networks = ["defaultNetwork", "net5G"]  # Define the network types
        results = []
        # Perform network requests
        for code, label in datanat_codes_labels:
            for network in networks:
                url = f'{base_url}?cNat={code}&cNet={network}&cInt=defaultDataInter'
                response = requests.get(url)                
                if response.status_code == 200:
                    data = response.json()
                    # Format the price to a float with two decimal places
                    price = data["data"]["redOneOfferConfiguration"]["pricePerMonthWithDiscount"] / 100.0
                    with5G = data["data"]["redOneOfferConfiguration"]["with5G"]
                    # Append data excluding code and network type, with formatted price
                    results.append((label, price, with5G))
                else:
                    logging.error(f"Failed to retrieve data for {code} ({label}) on {network}. Status code: {response.status_code}")        
        # Process the results for comparison and exclusion
        final_results = []
        for i in range(0, len(results), 2):
            if results[i][1] == results[i+1][1] and results[i][2] == results[i+1][2]:
                # Append the result with formatted price directly
                final_results.append((results[i][0], "{:.2f}".format(results[i][1]), results[i][2]))
            else:
                # Append both results with formatted prices directly
                final_results.append((results[i][0], "{:.2f}".format(results[i][1]), results[i][2]))
                if i+1 < len(results):
                    final_results.append((results[i+1][0], "{:.2f}".format(results[i+1][1]), results[i+1][2]))
        # Example of adding processed data to self.plans
        for name, price, is_5g in final_results:
            name = name
            price = price
            is_5g = is_5g
            self.plans.append({'name': name, 'price': price, 'is_5g': is_5g})        
        logging.info(f"Processed {len(self.plans)} plans for RED.")

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for RED.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            # Extract data attributes needed for database insertion
            # Simplified example; adjust based on actual data structure and database schema
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g, 0, 0, 0, 'NULL')
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")
        logging.info("Data insertion for RED completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Red()
    scraper.run()            

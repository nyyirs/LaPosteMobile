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

class Orange(BaseScraper):
    def __init__(self):
        super().__init__("Orange")
        logging.info("Initialized Orange Scraper Avec Engagement.")

    def scrape_data(self):
        """Scrape plan data from Orange's website."""
        logging.info("Scraping data from Orange.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from Orange.")

    def extract_plan_info_with_duration_marker(self, plans):
        extracted_info = []
    
        for plan in plans:
            # Data volume and technology extraction
            data_vol_tech = plan.split("Forfait ")[1].split(" ")[0]
            data_vol_tech_str = data_vol_tech        
            # Price extraction with duration distinction
            if 'puis' in plan:
                # For plans with a different price after 6 months
                price_6mo = plan.split('€ par mois pendant 6 mois puis')[0].split()[-1].replace(",", ".")
                price_after = plan.split('puis')[1].split('€')[0].strip().replace(",", ".")
                extracted_info.append({'name': data_vol_tech_str, 'is_5g': True, 'price': price_6mo, 'annee': 0.5})  # 1 for the first 6 months
                extracted_info.append({'name': data_vol_tech_str, 'is_5g': True, 'price': price_after, 'annee': 2})  # 2 for after 6 months
            else:
                # Single price throughout
                price = float(plan.split('€ par mois')[0].split()[-1].replace(",", "."))
                extracted_info.append({'name': data_vol_tech_str, 'is_5g': True, 'price': price, 'annee': 2})
        return extracted_info   

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Orange.")
        self.plans = []
        names = self.soup.find_all(class_="offer-tile")
        alt_names = [item.text for item in names if item]
        filtered_plan_names = [plan for plan in alt_names if " false " in plan and "24 mois " in plan] 
        self.final_list_with_duration_marker = self.extract_plan_info_with_duration_marker(filtered_plan_names)

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Orange.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.final_list_with_duration_marker:
            limite, unite = plan['name'][:-2].replace(' ',''), plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g, 0, 0, 1, plan['annee'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']} with engagement 1 with annee {plan['annee']}")
        logging.info("Data insertion for Orange completed.")

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#     scraper = Orange()
#     scraper.run()         




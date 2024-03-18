# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 14:48:05 2024

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

class Sfr(BaseScraper):
    def __init__(self):
        super().__init__("SFR")
        logging.info("Initialized SFR Scraper Deja Client.")

    def scrape_data(self):
        """Scrape plan data from SFR's website."""
        logging.info("Scraping data from SFR.")
        url = self.operator_data['URLDejaClient']  # Adjust based on actual key name
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
        names = self.soup.find_all('a', class_="title")
        alt_names = [item.text for item in names if item]        
        pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
        extracted_texts = [item.strip().replace('5G', '').replace('4G+', '').replace('4G', '') for item in alt_names if pattern.search(item)]  
            
        pattern_5g = re.compile(r"5G")
        extracted_5g = [bool(pattern_5g.search(text)) for text in alt_names if text.strip()]  

        engagements_list = self.soup.find_all('p', class_="engagement")
        alt_engagements = [item.text for item in engagements_list if item]
        engagement_elements = ['Engagement' in text for text in alt_engagements]

        price = self.soup.find_all('div', class_="pc")
        alt_prices = [item.text for item in price if item] 

        pattern = re.compile(r'(\d+,\d+|\d)[€].*?(\d+) mois puis (\d+,\d+)[€]|(\d+,\d+|\d)[€].*?(\d+) mois|(\d+,\d+|\d)[€]')

        # Process each string to extract the needed information
        extracted_prices = []
        for info in alt_prices:
            matches = pattern.findall(info)
            for match in matches:
                if match[1]:  # Found the pattern with months and subsequent price
                    extracted_prices.append({'months': int(match[1]), 'initial_price': match[0], 'subsequent_price': match[2]})
                elif match[4]:  # Found the pattern with just months (no subsequent price mentioned)
                    extracted_prices.append({'months': int(match[4]), 'initial_price': match[3], 'subsequent_price': None})
                else:  # Found the pattern with no months mentioned, implying a constant price
                    extracted_prices.append({'months': None, 'initial_price': match[5], 'subsequent_price': None})
        for name, price, is_5g, is_engagement in zip(extracted_texts, extracted_prices, extracted_5g, engagement_elements):
            match = re.match(r'((?:\d+H\s*)?\d+)\s*(Go|Mo)', name, re.IGNORECASE)
            if match:
                limite = match.group(1)  # Extract and strip to remove leading/trailing spaces
                unite = match.group(2) 

            if(price['months'] == None and price['subsequent_price'] == None):
                self.plans.append({
                    'Donnees': limite,
                    'unite': unite,
                    'price': price['initial_price'].replace(',','.'),
                    'avecEngagement': is_engagement, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': 2
                    })  

            else:
                self.plans.append({
                    'Donnees': limite,
                    'unite': unite,
                    'price': price['initial_price'].replace(',','.'),
                    'avecEngagement': is_engagement, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': float(price['months']) / 12
                    })
                self.plans.append({
                    'Donnees': limite,
                    'unite': unite,
                    'price': price['subsequent_price'].replace(',','.'),
                    'avecEngagement': is_engagement, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': 2
                    })   
                
    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], plan['Donnees'],  plan['unite'], plan['is_5g'], 0 , 0 , plan['avecEngagement'], plan['annee'], plan['deja_client'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['Donnees']} with price {plan['price']}")
        logging.info("Data insertion for SFR Mobile completed.")        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Sfr()
    scraper.run()                 
        

        
      
          
             


 




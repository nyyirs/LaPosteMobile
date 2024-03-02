# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:08:58 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import datetime
import logging
import re
from modules.base_scraper import BaseScraper

class Prixtel(BaseScraper):
    def __init__(self):
        super().__init__("Prixtel")
        logging.info("Initialized Prixtel Scraper.")

    def scrape_data(self):
        """Scrape plan data from Prixtel's website."""
        logging.info("Scraping data from Prixtel.")
        url = self.operator_data['URLSansEngagement']  # Adjust based on actual key name
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from {url} with status code {response.status_code}.")
            raise Exception(f"Failed to fetch data from {url}")
        self.soup = BeautifulSoup(response.content, 'html.parser')
        logging.info("Successfully scraped data from Prixtel.")
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Prixtel.")
        self.plans = []
        # Find all <li> elements with class 'wpx_prod'
        wpx_prod_elements = self.soup.find_all("li", class_="wpx_prod")        
        # Initialize a list to hold the extracted URLs
        urls = []        
        # Loop through each found element to extract the URL from the <a> tag
        for element in wpx_prod_elements:
            a_tag = element.find("a")  # Find the <a> tag within the current <li> element
            if a_tag and a_tag.has_attr("href"):  # Check if the <a> tag exists and has an 'href' attribute
                urls.append('https://www.prixtel.com' + a_tag['href'])  # Add the URL to the list  
        extracted_name = []
        extracted_price = []
        extracted_network = []
        # Print or process the extracted URLs
        # Assuming 'urls' is your list of URLs
        for new_url in urls:
            new_response = requests.get(new_url)
            new_soup = BeautifulSoup(new_response.text, 'lxml')  # Use response.text to get the HTML content            
            # Extracting names
            names = new_soup.find_all(class_="box")[1:]
            alt_names = [plan.text for plan in names if plan.text]  
            extracted_name.append(alt_names)            
            # Extracting prices
            prices = new_soup.find_all(class_="col2 off-promo")
            for price_group in prices:
                cleaned_str = price_group.text.replace('€', '').replace(' ', '').replace(',','.').split("/mois") # Remove '€' and '/mois'
                extracted_price.append(cleaned_str)            
            #is5g    
            text_5g = new_soup.find_all(class_="header_content")
            pattern_5g = re.compile(r"5G")
            extracted_5g = [bool(pattern_5g.search(text.text)) for text in text_5g]
            extracted_network.append(extracted_5g)            
        # Flatten the is_5g list for easier access
        list3_flattened = [item for sublist in extracted_network for item in sublist]
        # Iterate through each sublist
        for i in range(len(extracted_name)):
            # Assuming each sublist in list1, list2 has the same length and corresponds to each other
            for plan, price in zip(extracted_name[i], extracted_price[i]):
                if price:  # Ignore empty prices       
                    self.plans.append({'name': plan, 'is_5g': list3_flattened[i], 'price': price})
        logging.info(f"Processed {len(self.plans)} plans for Prixtel.")                 

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Prixtel.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")
        logging.info("Data insertion for Prixtel completed.")
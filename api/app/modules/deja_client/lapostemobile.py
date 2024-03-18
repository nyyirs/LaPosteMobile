# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 15:30:01 2024

@author: Nyyir
"""
from bs4 import BeautifulSoup
import datetime
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sys
import os
import time

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_scraper import BaseScraper

class Lapostemobile(BaseScraper):
    def __init__(self):
        super().__init__("La Poste Mobile")
        logging.info("Initialized La Poste Mobile Scraper Deja Client.")

    def scrape_data(self):
        """Scrape plan data from La Poste Mobile's website."""
        logging.info("Scraping data from La Poste Mobile.")
        self.url = self.operator_data['URLDejaClient'].split(';')  # Make sure this is correctly assigned    
        chrome_options = Options()
        # Uncomment the next line if you need a headless browser
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore-certificate-errors')
        # Custom user agent to mimic a real user visit
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])    
        try:
            # Setup WebDriver
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            self.driver.get(self.url[0])    
            # Wait for the specific element to be loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
            ).click() 
            logging.info("Successfully scraped data from La Poste Mobile.")            
        except Exception as e:
            logging.error(f"An error occurred while scraping data from La Poste Mobile: {e}")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for La Poste Mobile.")
        self.plans = [] 

        #--------Sans Engagement---------------
        pattern = re.compile(r"\b\d+(?:Go|Mo)\b")

        # Locate elements by ID
        name_elements = self.driver.find_elements(By.ID, "imgCaracteristique")

        # Extract matching parts of the 'alt' attribute of each element
        extracted_names = []
        for element in name_elements:
            alt_text = element.get_attribute('alt')  # Get the 'alt' attribute
            match = pattern.search(alt_text)  # Search for the pattern in the 'alt' text
            if match:
                extracted_names.append(match.group(0))  # If a match is found, add it to the list

        price_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.f12.h20')
        alt_prices = [element.text.split(':')[1].strip().replace('€', '.').replace('/mois', '') for element in price_elements if element.text]

        pattern_5g = re.compile(r"5G")
        extracted_5g = [bool(pattern_5g.search(text.get_attribute('alt'))) for text in name_elements if text.get_attribute('alt').strip()]


        for name, is_5g, price in zip(extracted_names, extracted_5g, alt_prices):
            self.plans.append({
                'Donnees': name[:-2],
                'unite': name[-2:],
                'price': price,
                'avecEngagement': 0, 
                'is_5g': is_5g,
                'deja_client': 1
                })

        #--------Avec Engagement---------------
        self.driver.get(self.url[1])

        pattern = re.compile(r"\b\d+(?:Go|Mo)\b")

        # Locate elements by ID
        name_elements = self.driver.find_elements(By.ID, "imgCaracteristique")

        # Extract matching parts of the 'alt' attribute of each element
        extracted_names = []
        for element in name_elements:
            alt_text = element.get_attribute('alt')  # Get the 'alt' attribute
            match = pattern.search(alt_text)  # Search for the pattern in the 'alt' text
            if match:
                extracted_names.append(match.group(0))  # If a match is found, add it to the list

        price_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.f12.h20')
        alt_prices = [element.text.split(':')[1].strip().replace('€', '.').replace('/mois', '') for element in price_elements if element.text]

        pattern_5g = re.compile(r"5G")
        extracted_5g = [bool(pattern_5g.search(text.get_attribute('alt'))) for text in name_elements if text.get_attribute('alt').strip()]


        for name, is_5g, price in zip(extracted_names, extracted_5g, alt_prices):
            self.plans.append({
                'Donnees': name[:-2],
                'unite': name[-2:],
                'price': price,
                'avecEngagement': 1, 
                'is_5g': is_5g,
                'deja_client': 1
                })
            
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "lblSwitch"))
        ).click()   

        time.sleep(2)

        pattern = re.compile(r"\b\d+(?:Go|Mo)\b")

        # Locate elements by ID
        name_elements = self.driver.find_elements(By.ID, "imgCaracteristique")

        # Extract matching parts of the 'alt' attribute of each element
        extracted_names = []
        for element in name_elements:
            alt_text = element.get_attribute('alt')  # Get the 'alt' attribute
            match = pattern.search(alt_text)  # Search for the pattern in the 'alt' text
            if match:
                extracted_names.append(match.group(0))  # If a match is found, add it to the list

        price_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.f12.h20')
        alt_prices = [element.text.split(':')[1].strip().replace('€', '.').replace('/mois', '') for element in price_elements if element.text]

        pattern_5g = re.compile(r"5G")
        extracted_5g = [bool(pattern_5g.search(text.get_attribute('alt'))) for text in name_elements if text.get_attribute('alt').strip()]


        for name, is_5g, price in zip(extracted_names, extracted_5g, alt_prices):
            self.plans.append({
                'Donnees': name[:-2],
                'unite': name[-2:],
                'price': price,
                'avecEngagement': 1, 
                'is_5g': is_5g,
                'deja_client': 1
                }) 

        self.driver.quit()

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], plan['Donnees'],  plan['unite'], plan['is_5g'], 0 , 0 , plan['avecEngagement'], 2, plan['deja_client'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['Donnees']} with price {plan['price']}")
        logging.info("Data insertion for La Poste Mobile completed.")        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Lapostemobile()
    scraper.run()      
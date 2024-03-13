# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 10:20:38 2024

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

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from base_scraper import BaseScraper

class sosh(BaseScraper):
    def __init__(self):
        super().__init__("Sosh")
        logging.info("Initialized Sosh mobile Scraper Fixe.")

    def scrape_data(self):
        """Scrape plan data from Sosh mobile's website."""
        logging.info("Scraping data from Sosh mobile.")
        url = self.operator_data['URLFixe']  # Make sure this is correctly assigned    
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
            self.driver.get(url)    
            # Wait for the specific element to be loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
            ).click() 
            logging.info("Successfully scraped data from Sosh mobile.")            
        except Exception as e:
            logging.error(f"An error occurred while scraping data from Sosh mobile: {e}")

        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Sosh mobile.")
        self.plans = [] 
        name = self.driver.find_elements(By.CSS_SELECTOR, 'h1.mw-100.mb-0.mb-lg-2')[0].text.split(':')[0]
        comment = self.driver.find_element(By.CSS_SELECTOR, 'span.price-promo-duration.pb-0').get_attribute('textContent').strip()
        price_mois = self.driver.find_element(By.CSS_SELECTOR, 'span.price-amount').get_attribute('textContent').strip().replace(',', '.').replace(' €', '')
        an = int(comment.split('mois puis')[0].replace('pendant', '').strip()) / 12
        price_an = comment.split('mois puis')[1].replace(',', '.').replace(' €', '').strip()
        self.plans.append({'name': name, 'annee': an, 'price': price_mois, 'adsl': 0, 'fibre': 1, 'is_5g': 0, 'avecEngagement': 0 })
        self.plans.append({'name': name, 'annee': 1, 'price': price_an, 'adsl': 0, 'fibre': 1, 'is_5g': 0, 'avecEngagement': 0 })
        # ADSL section
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "pills-adsl-tab"))
        ).click() 
        price_an_adsl = self.driver.find_element(By.XPATH, '//*[@id="pills-adsl"]/div[1]/div/div/div[1]/p/span[2]').get_attribute('textContent').strip().replace(',', '.').replace(' €', '')
        self.plans.append({'name': name, 'annee': 1, 'price': price_an_adsl, 'adsl': 1, 'fibre': 0, 'is_5g': 0, 'avecEngagement': 0 })
        self.driver.quit()

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Sosh.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], plan['name'].strip(), 'NULL', plan['is_5g'], plan['adsl'], plan['fibre'], plan['avecEngagement'], plan['annee'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name'].strip()} with price {plan['price']}")
        logging.info("Data insertion for Sosh completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = sosh()
    scraper.run()           


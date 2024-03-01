# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 21:25:29 2024

@author: Nyyir
"""

import datetime
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from base_scraper import BaseScraper
import json

class Lebara(BaseScraper):
    def __init__(self):
        super().__init__("Lebara")
        logging.info("Initialized Lebara Scraper.")

    def scrape_data(self):
        """Scrape plan data from Lebara's website."""
        logging.info("Scraping data from Lebara.")
        url = self.operator_data['URLSansEngagement']  # Make sure this is correctly assigned
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
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(url) 
            # Get the page source and parse it with BeautifulSoup
            self.page_source = driver.page_source
            logging.info("Successfully scraped data from Lebara.")
        except Exception as e:
            logging.error(f"An error occurred while scraping data from Lebara: {e}")
        finally:
            driver.quit()
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Lebara.")
        self.plans = [] 
        start = r'<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">'
        end = r'</pre></body></html>'
        # Use a regular expression to find all text between the start and end strings
        match = re.search(f'{re.escape(start)}(.*?){re.escape(end)}', self.page_source, re.DOTALL)
        # Check if a match was found
        if match:
            try:
                # Correctly use json.loads to parse the extracted string into a Python object
                extracted_text = json.loads(match.group(1))  # The captured text between the start and end strings
            except json.JSONDecodeError as e:
                logging.error("Failed to parse JSON:", e)
        else:
            logging.error("No match found.")
        new_data = extracted_text[':items']['root'][':items']['responsivegrid'][':items']['detailedviewplans_co']['offers']
        for item in new_data:
            self.plans.append({'name': item['planName'].split(" ")[2], 'is_5g': False, 'price': item['cost'].replace(',','.')})  

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Reglo Mobile.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g)
            self.db_operations.insert_into_tarifs(self.operator_data['OperateurID'], forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")
        logging.info("Data insertion for Reglo Mobile completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Lebara()
    scraper.run() 
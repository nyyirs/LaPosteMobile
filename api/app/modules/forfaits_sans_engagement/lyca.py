# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 06:14:16 2024

@author: Nyyir
"""

from bs4 import BeautifulSoup
import logging
import datetime
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

class Lyca(BaseScraper):
    def __init__(self):
        super().__init__("Lyca Mobile")
        logging.info("Initialized Lyca Mobile Scraper.")

    def scrape_data(self):
        """Scrape plan data from Lyca Mobile's website."""
        logging.info("Scraping data from Lyca Mobile.")
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
            WebDriverWait(driver, 10).until(
                   EC.element_to_be_clickable((By.ID , 'onetrust-accept-btn-handler'))
            ).click()
            # Get the page source and parse it with BeautifulSoup
            page_source = driver.page_source
            self.soup = BeautifulSoup(page_source, 'lxml')
            logging.info("Successfully scraped data from Lyca Mobile.")
        except Exception as e:
            logging.error(f"An error occurred while scraping data from Lyca Mobile: {e}")
        finally:
            driver.quit()
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Lyca Mobile.")
        self.plans = [] 
        names = self.soup.find_all(class_="PlanCard_plans_top_sec__En3Tq")
        alt_names = [plan.text.split('Data')[0].replace(' ', '') for plan in names if plan.text]
        alt_prices = [plan.text.split('Data')[1].replace(' ', '').split('€')[0] for plan in names if plan.text]        
        network = self.soup.find_all(class_="PlanCard_high_light__tLhfx")
        alt_network = ["5G" in net.text for net in network]
        for name, is5g, price in zip(alt_names, alt_network, alt_prices):
            self.plans.append({'name': name.replace(" ", ""), 'is_5g': is5g, 'price': price})        
        logging.info(f"Processed {len(self.plans)} plans for Lyca Mobile.")

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Lyca Mobile.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g, 0, 'NULL')
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")
        logging.info("Data insertion for Lyca Mobile completed.") 

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Lyca()
    scraper.run()                 
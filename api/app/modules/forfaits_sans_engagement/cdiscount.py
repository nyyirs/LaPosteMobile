# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 21:28:32 2024

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

class Cdiscount(BaseScraper):
    def __init__(self):
        super().__init__("Cdiscount mobile")
        logging.info("Initialized Cdiscount mobile Scraper Sans Engagement.")

    def scrape_data(self):
        """Scrape plan data from Cdiscount mobile's website."""
        logging.info("Scraping data from Cdiscount mobile.")
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
            # Wait for the specific element to be loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cmob2023__vignette__forfait__gigas"))
            )    
            # Get the page source and parse it with BeautifulSoup
            page_source = driver.page_source
            self.soup = BeautifulSoup(page_source, 'html.parser')            
            logging.info("Successfully scraped data from Cdiscount mobile.")            
        except Exception as e:
            logging.error(f"An error occurred while scraping data from Cdiscount mobile: {e}")
        finally:
            driver.quit()
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Cdiscount mobile.")
        self.plans = [] 
        names = self.soup.find_all(class_="cmob2023__vignette__forfait__gigas")
        alt_names = [plan.text.strip().replace(' ', '') for plan in names if plan.text.strip()]
        prices = self.soup.find_all(class_="cmob2023__vignette__forfait__price")
        alt_prices = [price.text for price in prices if price.text]   
        # Applying the function to each item in the alt_prices list
        cleaned_prices = [self.format_price(price) for price in alt_prices]
        # Find all <div> elements with the specified class
        divs = self.soup.find_all("div", class_="cmob2023fInfos__picto__gigas")
        # Initialize a list to hold the extracted data
        network_data = []
        # Compile regex pattern to match 'f_4g' or 'f_5g'
        pattern = re.compile(r'f-(4g|5g)')
        # Loop through each <div> element to find <img> tags and use regex to check the 'src' attribute
        for div in divs:
            img = div.find("img")
            if img:
                match = pattern.search(img['src'])
                if match:
                    # Determine True for 'f_5g', False for 'f_4g'
                    is_5g = match.group(1) == '5g'
                    network_data.append(is_5g)
        for name, is5g, price in zip(alt_names, network_data, cleaned_prices):
            self.plans.append({'name': name, 'is_5g': is5g, 'price': price})
        logging.info(f"Processed {len(self.plans)} plans for Cdiscount mobile.")

    def format_price(self, price_str):
        # Removing all whitespace characters and then reconstructing the expected format
        clean_price = ''.join(price_str.split())  # This removes all forms of whitespace
        # Extract digits for formatting
        digits = ''.join(filter(str.isdigit, clean_price))        
        if len(digits) > 2:
            # Insert a '.' before the last two digits (cents) for prices with cents
            formatted_price = f"{digits[:-2]}.{digits[-2:]}"
        elif len(digits) == 2 or len(digits) == 1:
            # Handle cases with only cents (or single digit prices) by assuming they are less than 1 euro
            formatted_price = f"{digits}"
        else:
            # Fallback for any other unexpected case, though this should be rare
            formatted_price = f"{digits}"    
        return formatted_price

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Cdiscount mobile.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            limite, unite = plan['name'][:-2], plan['name'][-2:]
            compatible5g = 1 if plan['is_5g'] else 0
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], limite, unite, compatible5g, 0, 0, 0, 'NULL')
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']} with is5G {plan['is_5g']}")
        logging.info("Data insertion for Cdiscount mobile completed.")

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#     scraper = Cdiscount()
#     scraper.run()           
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 16:05:32 2024

@author: Nyyir
"""

import datetime
import logging
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

class free(BaseScraper):
    def __init__(self):
        super().__init__("Free")
        logging.info("Initialized Free Scraper Sans Engagement.")

    def scrape_data(self):
        """Scrape plan data from Free's website."""
        logging.info("Scraping data from Free.")
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
            self.names = self.driver.find_elements(By.CSS_SELECTOR, 'span.text-center.font-iliad.font-regular.text-32')
            self.mois_price_decimal = self.driver.find_elements(By.CSS_SELECTOR, 'span.whitespace-nowrap.font-iliad.text-red')
            self.annee = self.driver.find_elements(By.CSS_SELECTOR, 'p.text-12.m-0.h-4')         
            logging.info("Successfully scraped data from Free.")            
        except Exception as e:
            logging.error(f"An error occurred while scraping data from Free: {e}")
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Free.")
        self.plans = [] 
        # Extract text from each element
        price=[]
        for element in self.mois_price_decimal:
            # Print the text, using .get_attribute('textContent') to include text from child nodes like <br>
            price.append(element.get_attribute('textContent'))    
        formatted_prices = []
        # Iterate over the list in steps of 2 to pair the euro and cent amounts
        for i in range(0, len(price), 2):
            # Replace the '€' with '.', join the pair into a single string, and add to the list
            formatted_prices.append(price[i] + '.' + price[i+1].replace('€', ''))
        # Use the zip function to iterate over the three lists simultaneously
        for name, price, an in zip(self.names, formatted_prices, self.annee):
            # Extract the text content from each WebElement
            name_text = name.get_attribute('textContent').strip()
            an_text_content = an.get_attribute('textContent')    
            if len(an_text_content) < 1:
                # If 'an' element is empty, use default values for the plan
                plan = {
                    'name': name_text,
                    'annee': 2,  # Default value if 'annee' is not specified
                    'price': price,  # Use the original price
                    'adsl': 0,  # Assuming all plans are fibre
                    'fibre': 1,
                    'is_5g': 0,
                    'avecEngagement': 0
                }
                self.plans.append(plan)
            else:
                # Split the 'an' text content to extract year and new price, if specified
                parts = an_text_content.split('an puis')
                an_text = parts[0].replace('pendant ', '').strip()
                # Default to 2 if 'an_text' isn't purely digits (implying a formatting issue or unexpected content)
                an_year = int(an_text) if an_text.isdigit() else 2        
                # Only proceed with new price extraction if 'an puis' was found and a second part exists
                if len(parts) > 1:
                    new_price_text = parts[1]
                    if '€/mois' in new_price_text:
                        new_price = new_price_text.split('€/mois')[0].replace(',', '.').strip()
                    else:
                        new_price = price  # Fallback to the original price if formatting is unexpected
                else:
                    new_price = price  # No new price specified, use the original
                # Initial period plan
                plan_initial = {
                    'name': name_text,
                    'annee': an_year,
                    'price': price,
                    'adsl': 0,
                    'fibre': 1,
                    'is_5g': 0,
                    'avecEngagement': 0
                }
                self.plans.append(plan_initial)        
                # If a new price is specified and different from the initial price, add a subsequent period plan
                if new_price != price:
                    plan_subsequent = {
                        'name': name_text,
                        'annee': 2,  # Assuming a two-year plan for the subsequent period
                        'price': new_price,
                        'adsl': 0,
                        'fibre': 1,
                        'is_5g': 0,
                        'avecEngagement': 0
                    }
                    self.plans.append(plan_subsequent)
        self.driver.quit()                    

    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database for Free.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], plan['name'], 'NULL', plan['is_5g'], plan['adsl'], plan['fibre'], plan['avecEngagement'], plan['annee'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['name']} with price {plan['price']}")
        logging.info("Data insertion for Free completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = free()
    scraper.run()     
 
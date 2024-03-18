# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 05:22:24 2024

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

class Byou(BaseScraper):
    def __init__(self):
        super().__init__("B&You")
        logging.info("Initialized B&You mobile Scraper Deja Client.")

    def scrape_data(self):
        """Scrape plan data from B&You mobile's website."""
        logging.info("Scraping data from B&You mobile.")
        url = self.operator_data['URLDejaClient']  # Make sure this is correctly assigned    
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
                EC.presence_of_element_located((By.ID, "popin_tc_privacy_button_3"))
            ).click() 
            time.sleep(3) 
            # Get the page source and parse it with BeautifulSoup
            page_source = driver.page_source
            self.soup = BeautifulSoup(page_source, 'html.parser')            
            logging.info("Successfully scraped data from B&You mobile.")            
        except Exception as e:
            logging.error(f"An error occurred while scraping data from B&You mobile: {e}")
        finally:
            driver.quit()
        
    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for B&You mobile.")
        self.plans = [] 
        names = self.soup.find_all('p', class_="title")
        # Use any() to check if 'Go' or 'Mo' is in plan.text
        alt_names = [plan.text for plan in names if any(keyword in plan.text for keyword in ('Go', 'Mo'))]     

        descriptions = self.soup.find_all('div', class_="plan-price no-height")
        alt_descriptions = [plan.text.strip().split('mois') for plan in descriptions]  

        is_engagement = [any('Engagement' in part for part in description) for description in alt_descriptions]

        elements_with_class_tri_5g = self.soup.find_all(class_='tri-5g')
        # Generate a list of booleans indicating whether 'tri-5g' class was found
        is_5g = [bool(element) for element in elements_with_class_tri_5g]

        self.plans=[]
        for name, data, is_5g, is_engagement in zip(alt_names, alt_descriptions, is_5g, is_engagement):
            match = re.match(r'((?:\d+H\s*)?(?:\d+\s*à\s*\d+|\d+))\s*(Go|Mo)', name, re.IGNORECASE)
            if match:
                limite = match.group(1)  # Extract and strip to remove leading/trailing spaces
                unite = match.group(2) 
            
            if(len(data) > 5):
                #6mois
                self.plans.append({
                    'Donnees': limite,
                    'unite': unite,
                    'price': "{:.2f}".format(float(data[1].replace(' ','').replace('/','').replace('€','.'))),
                    'avecEngagement': is_engagement, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': float(data[2].split('Bboxx')[1].strip()) / 12
                    })
                #24mois
                self.plans.append({
                    'Donnees': limite,
                    'unite': unite,
                    'price': "{:.2f}".format(float(data[3].split(' ')[1].replace('puis','').strip().replace(',','.'))),
                    'avecEngagement': is_engagement, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': float(data[4].strip().replace('Engagement','').strip()) / 12
                    })   
            else:
                self.plans.append({
                    'Donnees': limite,
                    'unite': unite,
                    'price': "{:.2f}".format(float(data[0].strip().replace('/','').replace('€','.').replace(' ',''))),
                    'avecEngagement': is_engagement, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': float(data[2].strip().replace('Engagement','').strip()) / 12
                    })              
                
    def insert_data(self):
        """Insert processed plan data into the database."""
        logging.info("Inserting data into the database.")
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        for plan in self.plans:
            forfait_id = self.db_operations.insert_into_forfaits(self.operator_data['OperateurID'], plan['Donnees'],  plan['unite'], plan['is_5g'], 0 , 0 , plan['avecEngagement'], plan['annee'], plan['deja_client'])
            self.db_operations.insert_into_tarifs(forfait_id, plan['price'], date_enregistrement)
            logging.info(f"Inserted plan {plan['Donnees']} with price {plan['price']}")
        logging.info("Data insertion for B&You completed.")        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scraper = Byou()
    scraper.run()          
        
        
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 14:59:49 2024

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

class Free(BaseScraper):
    def __init__(self):
        super().__init__("Free")
        logging.info("Initialized Free mobile Scraper Deja Client.")

    def scrape_data(self):
        """Scrape plan data from Free mobile's website."""
        logging.info("Scraping data from Free mobile.")
        url = self.operator_data['URLDejaClient']  # Make sure this is correctly assigned    
        chrome_options = Options()
        # Uncomment the next line if you need a headless browser
        #chrome_options.add_argument('--headless')
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

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/section/section[1]/div[1]/nav/p[2]'))
            ).click()
            logging.info("Successfully scraped data from Free mobile.")            
        except Exception as e:
            logging.error(f"An error occurred while scraping data from Free mobile: {e}")

    def process_data(self):
        """Process scraped plan data."""
        logging.info("Processing scraped data for Free mobile.")
        self.plans = [] 
        name_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.flex.w-full.flex-1.flex-col.items-center.p-8')
        alt_names = [element.text.strip().split("\n")[1:3] for element in name_elements if element.text]

        new_names = []
        for name in alt_names:
            if len(name[0]) < 3:
                new_names.append(name[0] + name[1].replace('Internet','').replace('en 4G/4G+', ''))
            else:         
                new_names.append(name[1].replace('Internet','').replace('en 4G/4G+', '').strip())

        pattern_5g = re.compile(r"5G")
        extracted_5g = [bool(pattern_5g.search(text.text)) for text in name_elements if text.text] 

        big_price_element = self.driver.find_elements(By.CSS_SELECTOR, 'div.flex.w-min.items-center')
        big_prices = ["{:.2f}".format(float(element.text.strip().replace("\n",'').replace('/mois', '').replace('€','.'))) for element in big_price_element if element.text]

        info_element = self.driver.find_elements(By.CSS_SELECTOR, 'p.inline')
        alt_infos = [element.text.strip().split("\n") for element in info_element if element.text]


        price_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.mt-4.flex.flex-col.items-center')
        alt_prices = [element.text.strip().split("\n") for element in price_elements if element.text]
        for name, price, info, is_5g in zip(new_names, big_prices, alt_infos, extracted_5g):
            if('Freebox' in info[0] and 'Pop' not in info[0]):        
                self.plans.append({
                    'Donnees': name.strip()[:-2],
                    'unite': name.strip()[-2:],
                    'price': price,
                    'avecEngagement': 0, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': 2
                    })
            elif ('Forfait' in info[0]):
                self.plans.append({
                    'Donnees': name.strip()[:-2],
                    'unite': name.strip()[-2:],
                    'price': price,
                    'avecEngagement': 0, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': 1
                    })  
                self.plans.append({
                    'Donnees': name.strip()[:-2],
                    'unite': name.strip()[-2:],
                    'price': info[0].split('à')[1].strip().replace('€/mois', ''),
                    'avecEngagement': 0, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': 2
                    })
            elif ('Pop' in info[0]):
                self.plans.append({
                    'Donnees': name + ' (freebox Pop)',
                    'unite': 'Go',
                    'price': price,
                    'avecEngagement': 0, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': 1
                    })
                self.plans.append({
                    'Donnees': name + ' (freebox Ultra)',
                    'unite': 'Go',
                    'price': info[1].split('pour')[0].strip().replace('€/mois', ''),
                    'avecEngagement': 0, 
                    'is_5g': is_5g,
                    'deja_client': 1,
                    'annee': 1
                    }) 
        
        self.driver.quit()

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
    scraper = Free()
    scraper.run()         





















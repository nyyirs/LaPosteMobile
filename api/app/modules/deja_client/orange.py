# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 09:10:19 2024

@author: Nyyir
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re

chrome_options = Options()
# Uncomment the next line if you need a headless browser
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
# Custom user agent to mimic a real user visit
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])    

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get('https://boutique.orange.fr/mobile/offres?withOpenPrices=true')    
# Wait for the specific element to be loaded
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
).click() 

name_elements = driver.find_elements(By.CSS_SELECTOR, 'div.title-wrapper.brand-color.px-1.my-1.d-flex.flex-column')
alt_names = [element.text for element in name_elements if element.text]
pattern = re.compile(r"Forfait \d+h \d+Go|Forfait \d+Go 5G|Forfait \d+h \d+Mo|Forfait \d+Mo|Forfait \d+Go|Série Spéciale \d+Go 5G")

# Extracting text matches directly without substitution
extracted_texts = [re.search(pattern, plan).group(0) if re.search(pattern, plan) else None for plan in alt_names]
pattern = r'^.*?(\d)'
modified_texts = [re.sub(pattern, r'\1', text) for text in extracted_texts]   

pattern_5g = re.compile(r"5G")
extracted_5g = [bool(pattern_5g.search(text)) for text in alt_names if text] 


engagements_list = driver.find_elements(By.CSS_SELECTOR, 'div.tile-content')
alt_engagements = [item.text for item in engagements_list if item]
engagement_elements = ['Engagement' in text for text in alt_engagements]

price_elements = driver.find_elements(By.CSS_SELECTOR, 'div.ob1-price.ob1-price-compact')
alt_prices = [element.text.split("\n")[0] for element in price_elements if element.text]

# Array to hold the prices
prices = []
# Regular expression to match prices
price_pattern = r"\d+\.\d+"    
for item in alt_prices:
    # Find all price occurrences
    found_prices = re.findall(price_pattern, item)
    
    # Handling the case where there might be only one price mentioned
    if len(found_prices) == 1:
        prices.append([found_prices[0]])

    else:
        # Assuming the first price is for the first 6 months and the second for after
        prices.append([found_prices[0], found_prices[1]])

driver.quit()

plans=[]
for name, price, is_5g, is_engagement in zip(modified_texts, prices, extracted_5g, engagement_elements):
    match = re.match(r'((?:\d+h)?\s*\d+)\s*(Go|Mo)', name)
    if match:
        limite = match.group(1)  # Extract and strip to remove leading/trailing spaces
        unite = match.group(2)   

    if (len(price) == 1):
        
        plans.append({
            'Donnees': limite,
            'unite': unite,
            'price': price[0],
            'avecEngagement': is_engagement, 
            'is_5g': is_5g,
            'deja_client': 1,
            'annee': 0.5
            }) 
    else:
        plans.append({
            'Donnees': limite,
            'unite': unite,
            'price': price[0],
            'avecEngagement': is_engagement, 
            'is_5g': is_5g,
            'deja_client': 1,
            'annee': 0.5
            })
        plans.append({
            'Donnees': limite,
            'unite': unite,
            'price': price[1],
            'avecEngagement': is_engagement, 
            'is_5g': is_5g,
            'deja_client': 1,
            'annee': 2
            })        
            



















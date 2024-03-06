# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 14:51:25 2024

@author: nyyir.m.soobrattee
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


url = 'https://www.bouyguestelecom.fr/forfaits-mobiles/avec-engagement'
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

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get(url)    
# Wait for the specific element to be loaded
WebDriverWait(driver, 10).until(
       EC.element_to_be_clickable((By.ID , 'popin_tc_privacy_button_3'))
).click()

WebDriverWait(driver, 10).until(
       EC.visibility_of_element_located((By.XPATH , '//*[@id="btl-design"]/ng-component/main/section[3]/div/div/div/div/div/btl-plan-configurator/div/div/div/div[2]/div[1]/trg-toggle/div/div/label'))
).click()

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')  

driver.quit()

# Assuming soup is a BeautifulSoup object already defined and loaded with HTML content
names = soup.find_all('p', class_="title")
# Use any() to check if 'Go' or 'Mo' is in plan.text
alt_names = [plan.text for plan in names if any(keyword in plan.text for keyword in ('Go', 'Mo'))][:-2]


descriptions = soup.find_all('div', class_="plan-price no-height")
alt_descriptions = [plan.text for plan in descriptions][:-2]

# Function to dynamically correct and format the price information
def dynamic_price_correction(price_str):
    # Extract euros and cents, if available
    parts = price_str.split('€')
    euros = parts[0].strip()
    cents = '00'  # Default cents value
    if len(parts) > 1:
        cents_part = parts[1].split()[0]  # Extract first part after '€' which is considered as cents
        if cents_part:
            cents = cents_part
    # Format the price correctly, ensuring cents are two digits
    return f"{euros},{cents[:2]}"

# Function to split the strings and extract the price information with dynamic correction
def extract_price_info_corrected(input_list):
    extracted_prices = []
    for item in input_list:
        parts = item.split('puis\xa0')
        prices = []
        for part in parts:
            # Extract the price before '€' and apply dynamic correction
            price_str = part.split('Engagement')[0]  # Split by 'Engagement' to isolate the price part
            corrected_price = dynamic_price_correction(price_str)
            prices.append(corrected_price.replace(',/m','').replace(',','.'))
        # Append corrected prices for 6 months and 24 months to the result list
        extracted_prices.append((prices[0], prices[1]))
    return extracted_prices

# Applying the function to the input list
corrected_price_info = extract_price_info_corrected(alt_descriptions)


elements_with_class_tri_5g = soup.find_all(class_='tri-5g')
# Generate a list of booleans indicating whether 'tri-5g' class was found
is_5g = [bool(element) for element in elements_with_class_tri_5g][:-2]


Plan = []
for i, (prices, is5g, name) in enumerate(zip(corrected_price_info, is_5g, alt_names)):
    Plan.append([name, str(is5g), prices[0], 1])  # Price 1 with identifier 1
    Plan.append([name, str(is5g), prices[1], 2])  # Price 2 with identifier 2
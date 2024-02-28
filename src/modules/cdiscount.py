# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 21:28:32 2024

@author: Nyyir
"""

from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

search_value = 'cdiscount'
url = 'https://www.cdiscount.com/cdiscount-mobile/forfaits-mobile-sans-engagement/v-16401-16401.html'  # Directly use the URL

chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Setup WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get(url)


WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "cmob2023__vignette__forfait__gigas"))
)

# Get the page source and parse it with BeautifulSoup
page_source = driver.page_source

driver.quit()

soup = BeautifulSoup(page_source, 'lxml')

names = soup.find_all(class_="cmob2023__vignette__forfait__gigas")
alt_names = [plan.text.strip().replace(' ', '') for plan in names if plan.text.strip()]

prices = soup.find_all(class_="cmob2023__vignette__forfait__price")
alt_prices = [price.text for price in prices if price.text]

# Function to clean and format price strings
def format_price(price_str):
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

# Applying the function to each item in the alt_prices list
cleaned_prices = [format_price(price) for price in alt_prices]


# Find all <div> elements with the specified class
divs = soup.find_all("div", class_="cmob2023fInfos__picto__gigas")

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

extracted_data = []

for name, is5g, price in zip(alt_names, network_data, cleaned_prices):
    extracted_data.append((name, is5g, price))















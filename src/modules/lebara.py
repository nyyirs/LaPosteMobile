# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 21:25:29 2024

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
import json
url = 'https://www.lebara.fr/fr/prepaye.html'

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

driver.get('https://www.lebara.fr/fr/prepaye.model.json')

# Get the page source and parse it with BeautifulSoup
page_source = driver.page_source

driver.quit()

start = r'<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">'
end = r'</pre></body></html>'

# Use a regular expression to find all text between the start and end strings
match = re.search(f'{re.escape(start)}(.*?){re.escape(end)}', page_source, re.DOTALL)

# Check if a match was found
if match:
    try:
        # Correctly use json.loads to parse the extracted string into a Python object
        extracted_text = json.loads(match.group(1))  # The captured text between the start and end strings
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
else:
    print("No match found.")

new_data = extracted_text[':items']['root'][':items']['responsivegrid'][':items']['detailedviewplans_co']['offers']

extracted_data = []
for item in new_data:
    extracted_data.append((item['planName'].split(" ")[2], False, item['cost'].replace(',','.')))
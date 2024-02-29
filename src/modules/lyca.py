# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 06:14:16 2024

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

# response = requests.get('https://www.lycamobile.fr/fr/bundles/forfait-prepaye/')  

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
driver.get('https://www.lycamobile.fr/fr/bundles/forfait-prepaye/')


WebDriverWait(driver, 10).until(
       EC.element_to_be_clickable((By.ID , 'onetrust-accept-btn-handler'))
).click()

# Get the page source and parse it with BeautifulSoup
page_source = driver.page_source

driver.quit()

soup = BeautifulSoup(page_source, 'lxml')

names = soup.find_all(class_="PlanCard_plans_top_sec__En3Tq")
alt_names = [plan.text.split('Data')[0].replace(' ', '') for plan in names if plan.text]
alt_prices = [plan.text.split('Data')[1].replace(' ', '').split('€')[0] for plan in names if plan.text]

network = soup.find_all(class_="PlanCard_high_light__tLhfx")
alt_network = ["5G" in net.text for net in network]


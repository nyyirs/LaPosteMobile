# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 05:22:24 2024

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
from bs4 import BeautifulSoup

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
driver.get('https://www.bouyguestelecom.fr/forfaits-mobiles/avec-engagement')    
# Wait for the specific element to be loaded
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "popin_tc_privacy_button_3"))
).click() 

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "title"))
)
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')  

names = soup.find_all('p', class_="title")
# Use any() to check if 'Go' or 'Mo' is in plan.text
alt_names = [plan.text for plan in names if any(keyword in plan.text for keyword in ('Go', 'Mo'))]     

descriptions = soup.find_all('div', class_="plan-price no-height")
alt_descriptions = [plan.text.strip().split('mois') for plan in descriptions]  

is_engagement = [any('Engagement' in part for part in description) for description in alt_descriptions]

elements_with_class_tri_5g = soup.find_all(class_='tri-5g')
# Generate a list of booleans indicating whether 'tri-5g' class was found
is_5g = [bool(element) for element in elements_with_class_tri_5g]

plans=[]
for name, data, is_5g, is_engagement in zip(alt_names, alt_descriptions, is_5g, is_engagement):
    match = re.match(r'((?:\d+H\s*)?\d+)\s*(Go|Mo)', name, re.IGNORECASE)
    if match:
        limite = match.group(1)  # Extract and strip to remove leading/trailing spaces
        unite = match.group(2) 
    
    if(len(data) > 5):
        #6mois
        plans.append({
            'Donnees': limite,
            'unite': unite,
            'price': "{:.2f}".format(float(data[1].replace(' ','').replace('/','').replace('€','.'))),
            'avecEngagement': is_engagement, 
            'is_5g': is_5g,
            'deja_client': 1,
            'annee': float(data[2].split('Bboxx')[1].strip()) / 12
            })
        #24mois
        plans.append({
            'Donnees': limite,
            'unite': unite,
            'price': "{:.2f}".format(float(data[3].split(' ')[1].replace('puis','').strip().replace(',','.'))),
            'avecEngagement': is_engagement, 
            'is_5g': is_5g,
            'deja_client': 1,
            'annee': float(data[4].strip().replace('Engagement','').strip()) / 12
            })   
    else:
        plans.append({
            'Donnees': limite,
            'unite': unite,
            'price': "{:.2f}".format(float(data[0].strip().replace('/','').replace('€','.').replace(' ',''))),
            'avecEngagement': is_engagement, 
            'is_5g': is_5g,
            'deja_client': 1,
            'annee': float(data[2].strip().replace('Engagement','').strip()) / 12
            }) 
        
         
     
# driver.quit()
        
        
        
        
        
        
        
        
        
        
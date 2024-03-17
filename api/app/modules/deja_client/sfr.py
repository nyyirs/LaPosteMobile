# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 14:48:05 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.sfr.fr/offre-mobile'

response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')

names = soup.find_all('a', class_="title")
alt_names = [item.text for item in names if item]        
pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
extracted_texts = [item.strip().replace('5G', '').replace('4G+', '').replace('4G', '') for item in alt_names if pattern.search(item)]  
     
pattern_5g = re.compile(r"5G")
extracted_5g = [bool(pattern_5g.search(text)) for text in extracted_texts if text.strip()]  

engagements_list = soup.find_all('p', class_="engagement")
alt_engagements = [item.text for item in engagements_list if item]
engagement_elements = ['Engagement' in text for text in alt_engagements]

price = soup.find_all('div', class_="pc")
alt_prices = [item.text for item in price if item] 

pattern = re.compile(r'(\d+,\d+|\d)[€].*?(\d+) mois puis (\d+,\d+)[€]|(\d+,\d+|\d)[€].*?(\d+) mois|(\d+,\d+|\d)[€]')

# Process each string to extract the needed information
extracted_prices = []
for info in alt_prices:
    matches = pattern.findall(info)
    for match in matches:
        if match[1]:  # Found the pattern with months and subsequent price
            extracted_prices.append({'months': int(match[1]), 'initial_price': match[0], 'subsequent_price': match[2]})
        elif match[4]:  # Found the pattern with just months (no subsequent price mentioned)
            extracted_prices.append({'months': int(match[4]), 'initial_price': match[3], 'subsequent_price': None})
        else:  # Found the pattern with no months mentioned, implying a constant price
            extracted_prices.append({'months': None, 'initial_price': match[5], 'subsequent_price': None})
            
plans=[]
for name, price, is_5g, is_engagement in zip(extracted_texts, extracted_prices, extracted_5g, engagement_elements):
    match = re.match(r'((?:\d+H\s*)?\d+)\s*(Go|Mo)', name, re.IGNORECASE)
    if match:
        limite = match.group(1)  # Extract and strip to remove leading/trailing spaces
        unite = match.group(2) 

    if(price['months'] == None and price['subsequent_price'] == None):
        plans.append({
            'Donnees': limite,
            'unite': unite,
            'price': price['initial_price'],
            'avecEngagement': is_engagement, 
            'is_5g': is_5g,
            'deja_client': 1,
            'annee': 2
            })  

    else:
        plans.append({
            'Donnees': limite,
            'unite': unite,
            'price': price['initial_price'],
            'avecEngagement': is_engagement, 
            'is_5g': is_5g,
            'deja_client': 1,
            'annee': float(price['months']) / 12
            })
        plans.append({
            'Donnees': limite,
            'unite': unite,
            'price': price['subsequent_price'],
            'avecEngagement': is_engagement, 
            'is_5g': is_5g,
            'deja_client': 1,
            'annee': 2
            })   
        

        
      
          
             


 




# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 08:58:40 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
from modules.azure_sql_db import load_environment_variables, get_database_connection, fetch_operator_data, insert_into_forfaits, insert_into_tarifs

def soch():
    # Load environment variables
    load_environment_variables()
    
    # Establish database connection
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Define date of record
    date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Fetch operator data
    operator_data = fetch_operator_data(cursor, 'Sosh')
    url = operator_data[2]  # Assuming URLSansEngagement is the URL to parse
    
    # Parse plans data
    response = requests.get(url)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extracting titles
    names = soup.find_all(class_="title")
    alt_names = [plan.text for plan in names if "Bloqués" not in plan.text]
    
    # Extracting prices
    prices = soup.find_all(class_="price-amount")
    alt_prices = [item.text.strip() for item in prices if item]
    
    # Assuming you want to match specific patterns in the titles, for example, storage sizes
    pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
    extracted_texts = [pattern.search(text).group(0) for text in alt_names if pattern.search(text)]
    
    pattern_5g = re.compile(r"5G")
    extracted_5g = [bool(pattern_5g.search(text)) for text in alt_names if text.strip()]
    
    # Mapping titles to prices, assuming the lists align perfectly
    plan_prices = [price.replace("€","").replace(",",".") for price in alt_prices]
    
    OperateurID, NomOperateur, URLSansEngagement = operator_data
    
    for name, is_5g, price in zip(extracted_texts, extracted_5g, plan_prices):
        limite, unite = name[:-2], name[-2:]
        compatible5g = 1 if is_5g else 0
    
        if is_5g:
            forfait_id = insert_into_forfaits(cursor, OperateurID, limite, unite, compatible5g)
            conn.commit()  # Commit the Forfaits insert
            insert_into_tarifs(cursor, OperateurID, int(forfait_id), price, date_enregistrement)
            conn.commit()
        else:
            forfait_id = insert_into_forfaits(cursor, OperateurID, limite, unite, 0)
            conn.commit()  # Commit the Forfaits insert
            insert_into_tarifs(cursor, OperateurID, int(forfait_id), price, date_enregistrement)
            conn.commit()
    
    # Close connection
    conn.close()
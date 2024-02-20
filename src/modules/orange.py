# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 11:35:12 2024

@author: Nyyir
"""
import requests
from bs4 import BeautifulSoup
import re
import datetime
from modules.azure_sql_db import load_environment_variables, get_database_connection, fetch_operator_data, insert_into_forfaits, insert_into_tarifs

def orange():
    # Load environment variables
    load_environment_variables()
    
    # Establish database connection
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Define date of record
    date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Fetch operator data
    operator_data = fetch_operator_data(cursor, 'Orange')
    url = operator_data[2]  # Assuming URLSansEngagement is the URL to parse
    
    # Parse plans data
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract plan details
    names = soup.find_all(class_="offer-tile")
    alt_names = [item.text for item in names if item]
    filtered_plan_names = [plan for plan in alt_names if " false " in plan]
    
    pattern = re.compile(r"Forfait \d+h \d+Go|Forfait \d+Go 5G|Forfait \d+h \d+Mo|Forfait \d+Mo|Forfait \d+Go|Série Spéciale \d+Go 5G")
    extracted_texts = [re.search(pattern, plan).group(0) if re.search(pattern, plan) else None for plan in filtered_plan_names]
    
    pattern = r'^.*?(\d)'
    modified_texts = [re.sub(pattern, r'\1', text) for text in extracted_texts]
    
    # Extract the 5G
    pattern_5g = re.compile(r"5G")
    extracted_5g = [bool(pattern_5g.search(text)) for text in modified_texts if text.strip()]
    
    # Extract the price
    extracted_prices = []
    for plan in filtered_plan_names:
        match = re.search(r'(\d+,\d+)€', plan)
        if match:
            price = match.group(1).replace(",", ".")
            extracted_prices.append(f"{price}")
    
    # Assuming a missing piece in the original code for price replacement - it seems incomplete.
    # Assuming it should convert price to a format suitable for database insertion
    
    # Insert plans to database
    OperateurID, NomOperateur, URLSansEngagement = operator_data
    
    for name, is_5g, price in zip(modified_texts[2:], extracted_5g[2:], extracted_prices[2:]):
        match = re.match(r'((?:\d+h)?\s*\d+)\s*(Go|Mo)', name.strip())
        if match:
            limite = match.group(1).strip()  # Extract and strip to remove leading/trailing spaces
            unite = match.group(2).strip()
    
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

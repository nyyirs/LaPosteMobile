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

def sfr():
    try:
        # Load environment variables
        load_environment_variables()
        
        # Establish database connection
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Define date of record
        date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Fetch operator data
        operator_data = fetch_operator_data(cursor, 'SFR')
        url = operator_data[2]  # Assuming the URL is the third item in operator_data
        
        # Parse plans data
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract plan details
        names = soup.find_all(class_="title")
        alt_names = [item.text for item in names if item]
        
        pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
        extracted_texts = [item for item in alt_names if pattern.search(item)]
        
        pattern_5g = re.compile(r"5G")
        extracted_5g = [bool(pattern_5g.search(text)) for text in extracted_texts if text.strip()]
        
        prix_entier = soup.find_all(class_="L")
        prix_decimal = soup.find_all(class_="R")
        alt_prices = [item.text.strip() for item in prix_entier if item]
        alt_decimals = [item.text.strip() for item in prix_decimal if item]
        cleaned_list_decimals = [item for item in alt_decimals if item != '/mois']
        
        plan_prices = []
        for text, price, decimal in zip(extracted_texts, alt_prices, cleaned_list_decimals):
            if not decimal:
                decimal_part = ''
            else:
                match = re.search(r"(\d+)", decimal)
                decimal_part = match.group(1) if match else ''
            full_price = f"€{price}" + (f".{decimal_part}" if decimal_part else "")
            plan_prices.append(full_price)
        
        # Insert plans to database
        OperateurID, NomOperateur, URLSansEngagement = operator_data
        
        for name, is_5g, price in zip(extracted_texts[2:], extracted_5g[2:], plan_prices[2:]):
            match = re.match(r'([\d\sH]+)\s*(Go|Mo)', name.strip())
            if match:
                limite = match.group(1).strip()  # Extract and strip to remove leading/trailing spaces
                unite = match.group(2).strip()
        
            compatible5g = 1 if is_5g else 0
        
            if is_5g:
                forfait_id = insert_into_forfaits(cursor, OperateurID, limite, unite, compatible5g)
                conn.commit()  # Commit the Forfaits insert
                insert_into_tarifs(cursor, OperateurID, int(forfait_id), price.replace("€", ""), date_enregistrement)
                conn.commit()
            else:
                forfait_id = insert_into_forfaits(cursor, OperateurID, limite, unite, 0)
                conn.commit()  # Commit the Forfaits insert
                insert_into_tarifs(cursor, OperateurID, int(forfait_id), price.replace("€", ""), date_enregistrement)
                conn.commit()
        
        # Close connection
        conn.close()
        
        return NomOperateur + ' completed'
    except:
        return 'SFR failed'

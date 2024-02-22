# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 09:43:56 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
from modules.azure_sql_db import load_environment_variables, get_database_connection, fetch_operator_data, insert_into_forfaits, insert_into_tarifs

def free():
    # Load environment variables
    load_environment_variables()
    
    # Establish database connection
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Define date of record
    date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Fetch operator data
    operator_data = fetch_operator_data(cursor, 'Free')
    url = operator_data[2]  # Assuming URLSansEngagement is the URL to parse    
    
    # Parse plans data
    response = requests.get(url)
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    names = soup.find_all(class_="ml-4 text-14")
    alt_names = [item.text for item in names if item]
    
    # Define the regex pattern
    pattern = r"Internet\s(\d+)\s(Mo|Go)\sen\s([45]G\+?\/[45]G\+?)"
    extracted_names = list(set([match for text in alt_names for match in re.findall(pattern, text) if match]))
    # Sort first
    extracted_names.sort(key=lambda x: int(x[0]), reverse=True)
    # Then deduplicate, preserving order
    from collections import OrderedDict
    extracted_names = list(OrderedDict.fromkeys(extracted_names))
    
    
    prices = soup.find_all(class_="h-[min-content]")
    alt_prices = [item.text for item in prices if item][:3]
    
    prices_decimal = soup.find_all(class_="ml-1 self-start")
    alt_prices_decimal = [f".{item.text.replace('/mois','').replace('€','')}" if item.text.replace('/mois','').replace('€','').strip() else '' for item in prices_decimal if item][:3]
    
    final_list = [
        (f"{name[0]}{name[1]}", '5G' in name[2], f"{alt_prices[i]}{alt_prices_decimal[i]}") 
        for i, name in enumerate(extracted_names)
    ]
    
    # Insert plans to database
    OperateurID, NomOperateur, URLSansEngagement = operator_data
    
    for name, is_5g, price in final_list:
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

    return NomOperateur + ' completed'


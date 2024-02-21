# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 14:51:25 2024

@author: nyyir.m.soobrattee
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import datetime
from modules.azure_sql_db import load_environment_variables, get_database_connection, fetch_operator_data, insert_into_forfaits, insert_into_tarifs

def byou():
    load_environment_variables()
    
    # Establish database connection
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Define date of record
    date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Fetch operator data
    operator_data = fetch_operator_data(cursor, 'B&You')
    url = operator_data[2]  # Assuming URLSansEngagement is the URL to parse
    
    response = requests.get(url)  
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the <script> tag by ID for JSON data extraction
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    # Extract and parse the JSON string
    json_str = script_tag.string if script_tag else '{}'
    data = json.loads(json_str)
    
    other_offers = data['props']['pageProps']['productsList']['catalogue']
    
    main_offers = data['props']['pageProps']['productsList']['offers']
    
    # Process other_offers excluding the second item
    extracted_data_other_offers = []
    for i, offer in enumerate(other_offers):
        if i != 1:  # Skip the second item
            data_envelope = offer['data_envelope']
            newprice = offer['newprice']
            option5g_present = bool(offer.get('option5g'))
    
            if option5g_present:
                adjusted_price = newprice + offer['option5g']['price']
                extracted_data_other_offers.append((data_envelope, True, adjusted_price))
            else:
                extracted_data_other_offers.append((data_envelope, True, newprice))
            
            if option5g_present:
                extracted_data_other_offers.append((data_envelope, False, newprice))
    
    # Process main_offers
    extracted_data_main_offers = []
    for offer in main_offers:
        data_envelope = offer['data_envelope']
        newprice = offer['newprice']
        option5g_present = bool(offer.get('option5g'))
    
        if option5g_present:
            adjusted_price = newprice + offer['option5g']['price']
            extracted_data_main_offers.append((data_envelope, True, adjusted_price))
        else:
            extracted_data_main_offers.append((data_envelope, True, newprice))
        
        if option5g_present:
            extracted_data_main_offers.append((data_envelope, False, newprice))
    
    # Merge the two lists and convert entries to tuples
    merged_data_final = extracted_data_other_offers + extracted_data_main_offers
    
    OperateurID, NomOperateur, URLSansEngagement = operator_data
    
    for name, is_5g, price in merged_data_final:
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


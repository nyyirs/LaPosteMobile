# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 10:08:56 2024

@author: Nyyir
"""
import requests
from bs4 import BeautifulSoup
import json
import datetime
from modules.azure_sql_db import load_environment_variables, get_database_connection, fetch_operator_data, insert_into_forfaits, insert_into_tarifs

def red():
    # Load environment variables
    load_environment_variables()
    
    # Establish database connection
    conn = get_database_connection()
    cursor = conn.cursor()
    
    # Define date of record
    date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Fetch operator data
    operator_data = fetch_operator_data(cursor, 'RED')
    url = operator_data[2]  # Assuming URLSansEngagement is the URL to parse
    
    # Parse plans data
    response = requests.get(url)
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the <amp-state> tag with the specific ID 'serviceOffer'
    amp_state_tag = soup.find('amp-state', id='serviceOffer')
    
    # Extract the JSON string from the <script> tag within <amp-state> if present
    json_str = amp_state_tag.script.string if amp_state_tag and amp_state_tag.script else '{}'
    
    # Parse the JSON string into a Python dictionary
    data = json.loads(json_str)
    
    datanat_codes_labels = [(entry["code"], entry["label"]) for entry in data["data"]["redOneOfferConfiguration"]["datanat"]]
    
    
    # Base URL without query parameters
    base_url = 'https://api.red-by-sfr.fr/service-offer-red/api/rest/v1/mobile'
    
    # Networks to iterate over
    networks = ["defaultNetwork", "net5G"]  # Define the network types
    results = []
    
    # Perform network requests
    for code, label in datanat_codes_labels:
        for network in networks:
            url = f'{base_url}?cNat={code}&cNet={network}&cInt=defaultDataInter'
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # Format the price to a float with two decimal places
                price = data["data"]["redOneOfferConfiguration"]["pricePerMonthWithDiscount"] / 100.0
                with5G = data["data"]["redOneOfferConfiguration"]["with5G"]
                # Append data excluding code and network type, with formatted price
                results.append((label, price, with5G))
            else:
                print(f"Failed to retrieve data for {code} ({label}) on {network}. Status code: {response.status_code}")
    
    # Process the results for comparison and exclusion
    final_results = []
    for i in range(0, len(results), 2):
        if results[i][1] == results[i+1][1] and results[i][2] == results[i+1][2]:
            # Append the result with formatted price directly
            final_results.append((results[i][0], "{:.2f}".format(results[i][1]), results[i][2]))
        else:
            # Append both results with formatted prices directly
            final_results.append((results[i][0], "{:.2f}".format(results[i][1]), results[i][2]))
            if i+1 < len(results):
                final_results.append((results[i+1][0], "{:.2f}".format(results[i+1][1]), results[i+1][2]))
                
    OperateurID, NomOperateur, URLSansEngagement = operator_data
    
    for name, price, is_5g in final_results:
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




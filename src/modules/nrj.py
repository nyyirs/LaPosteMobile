# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 13:44:04 2024

@author: Nyyir
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def nrj(search_value, file_path):
    #search_value = 'Free'
    #file_path = 'info.xlsx'

    df = pd.read_excel(file_path, sheet_name='Sheet1')
    
    name_col_index = df.columns.get_loc('Name')
    next_col_name = df.columns[name_col_index + 1]
    url = df[df['Name'] == search_value][next_col_name].iloc[0]
    
    response = requests.get(url)
    
    # Ensure BeautifulSoup is used with the response content, specifying 'lxml' as the parser
    soup = BeautifulSoup(response.text, 'lxml')  # Use response.text to get the HTML content
    
    # Find all <a> tags
    a_tags = soup.find_all('a')
    
    # Initialize a list to hold all onclick attributes
    onclick_attributes = []
    
    # Iterate over all found <a> tags to extract 'onclick' attributes
    for a_tag in a_tags:
        onclick = a_tag.get('onclick')
        if onclick:  # Check if the onclick attribute exists
            onclick_attributes.append(onclick)
    
    # Loop through each function call
    extracted_data = {}
    
    for call in onclick_attributes:
        if "add_to_cart_click_product" in call:
            parts = call.split("'")
            forfait_name = parts[3]
            initial_price = parts[-1].split(",")[1]
    
            # Use regular expression to find patterns of digits followed by 'go' or 'mo'
            data_volume_matches = re.findall(r'\d+\s*go|\d+\s*mo', forfait_name, re.IGNORECASE)
    
            if data_volume_matches:
                data_volume = data_volume_matches[0].replace("go", "Go").replace("mo", "Mo").replace(" ", "")
                # Format the price by ensuring the "€" symbol is at the front
                price_formatted = "€" + initial_price
                extracted_data[data_volume] = price_formatted
    
    # Convert the extracted data into a DataFrame
    df_plans = pd.DataFrame([extracted_data], index=[search_value])
    
    return df_plans

# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 21:09:55 2024

@author: Nyyir
"""

import pandas as pd
import requests
from lxml import html


def free(search_value, file_path):
    #search_value = 'Free'
    #file_path = 'info.xlsx'

    df = pd.read_excel(file_path, sheet_name='Sheet1')
    
    name_col_index = df.columns.get_loc('Name')
    next_col_name = df.columns[name_col_index + 1]
    url = df[df['Name'] == search_value][next_col_name].iloc[0]
    
    response = requests.get(url)  
        
    tree = html.fromstring(response.content)
    
    # XPath to extract the text from
    
    xpath_info = [
        ("250GB", '//*[@id="__next"]/main/section/section[1]/ul/li[1]/div[1]/ul/li[1]/div/p/b', '//*[@id="__next"]/main/section/section[1]/ul/li[1]/div[2]/div/div[1]/span', '//*[@id="__next"]/main/section/section[1]/ul/li[1]/div[2]/div/div[1]/div/span[1]'),
        ("110GB", '//*[@id="__next"]/main/section/section[1]/ul/li[2]/div[1]/ul/li[1]/div/p/b', '//*[@id="__next"]/main/section/section[1]/ul/li[2]/div[2]/div/div[1]/span', '//*[@id="__next"]/main/section/section[1]/ul/li[2]/div[2]/div/div[1]/div/span[1]'),
        ("50GB", '//*[@id="__next"]/main/section/section[1]/ul/li[3]/div[1]/ul/li[1]/div/p/b[1]', '//*[@id="__next"]/main/section/section[1]/ul/li[3]/div[2]/div/div[1]/span', '//*[@id="__next"]/main/section/section[1]/ul/li[3]/div[2]/div/div[1]/div/span[1]')
    ]
    
    # Initialize an empty dictionary to store plan names and their prices
    plan_prices = {}
    
    # Function to format the price
    def format_price(price, decimal_price):
        # Remove any existing "€" symbol and strip whitespace
        price = price.replace("€", "").strip()
        decimal_price = decimal_price.replace("€", "").strip()
        
        # Concatenate price and decimal with a dot for the decimal separator
        # Ensure the decimal point is included even if decimal_price is an empty string or "00"
        if decimal_price == "" or decimal_price == "00":
            formatted_price = f"{price}"  # No need to add .00 if decimal part is 00 or empty
        else:
            formatted_price = f"{price}.{decimal_price}"
        
        # Place the "€" symbol in front of the formatted price
        return f"€{formatted_price}"
    
    # Iterate through each tuple in the xpath_info list
    for plan, feature_xpath, price_xpath, decimal_price_xpath in xpath_info:
        # Use the XPath to extract the feature text, price, and decimal part of the price
        feature_text = tree.xpath(feature_xpath + '/text()')
        price_text = tree.xpath(price_xpath + '/text()')
        decimal_price_text = tree.xpath(decimal_price_xpath + '/text()')
        
        # Check if all necessary information was successfully extracted
        if feature_text and price_text and decimal_price_text:
            extracted_feature_text = feature_text[0]
            extracted_price_text = price_text[0]
            extracted_decimal_price_text = decimal_price_text[0]
            
            # Format and store the price information
            formatted_price = format_price(extracted_price_text, extracted_decimal_price_text)
            plan_prices[extracted_feature_text] = formatted_price
        else:
            print(f"No complete information found for Plan: {plan}")
    
    # Creating a DataFrame from the extracted data
    df_plans = pd.DataFrame([plan_prices], index=[search_value])
    
    df_plans.columns = df_plans.columns.str.replace(' ', '')

    return df_plans

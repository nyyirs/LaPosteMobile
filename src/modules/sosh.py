# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 17:30:16 2024

@author: Nyyir
"""
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def sosh(search_value, file_path):
    """
    Extracts mobile plan details and pricing information based on a given search value.
    
    Parameters:
    - search_value: The name of the mobile plan or provider to search for in the DataFrame.
    - file_path: The path to the excel file to retrieve data from.
    
    Returns:
    - A DataFrame containing the name and price of mobile plans in one row, with plans as columns.
    """
   
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    
    name_col_index = df.columns.get_loc('Name')
    next_col_name = df.columns[name_col_index + 1]
    url = df[df['Name'] == search_value][next_col_name].iloc[0]
    
    response = requests.get(url)  
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extracting titles
    names = soup.find_all(class_="title")
    alt_names = [item.text for item in names if item]
    
    # Extracting prices
    prices = soup.find_all(class_="price-amount")
    alt_prices = [item.text.strip() for item in prices if item]
    
    # Assuming you want to match specific patterns in the titles, for example, storage sizes
    pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
    extracted_texts = [pattern.search(text).group(0) for text in alt_names if pattern.search(text)]
    
    # Mapping titles to prices, assuming the lists align perfectly
    plan_prices = {text: price for text, price in zip(extracted_texts, alt_prices)}
    
    # Creating a DataFrame from the extracted data
    df_plans = pd.DataFrame([plan_prices], index=[search_value])
    
    # Function to format the price
    def format_price(price):
        # Removing commas and moving the "€" sign to the front
        formatted_price = price.replace(',', '.').replace('€', '')
        return f"€{formatted_price}"
    
    # Applying the transformation to each value in the DataFrame
    for col in df_plans.columns:
        df_plans[col] = df_plans[col].apply(format_price)
    
    return df_plans


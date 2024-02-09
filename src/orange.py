# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def orange(search_value, file_path):
    """
    Extracts mobile plan details and pricing information based on a given search value.
    
    Parameters:
    - search_value: The name of the mobile plan or provider to search for in the DataFrame.
    - file_path: The path to the excel file to retrieve data from.
    
    Returns:
    - A DataFrame containing the name and price of mobile plans in one row, with plans as columns.
    """


    # Assume file_path and search_value are defined
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    
    name_col_index = df.columns.get_loc('Name')
    next_col_name = df.columns[name_col_index + 1]
    url = df[df['Name'] == search_value][next_col_name].iloc[0]
    
    response = requests.get(url)  
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    names = soup.find_all(class_="offer-tile")
    alt_names = [item.text for item in names if item]
    
    prices = soup.find_all(class_="ob1-price-amount")
    
    filtered_plans = [plan for plan in alt_names if " false " in plan]
    
    pattern = re.compile(r'(\d+Go|\d+Mo).*?(\d+,\d+€)')
    
    # Iterate over the filtered_plans list and apply the regex pattern to find matches
    extracted_data = {}
    for plan in filtered_plans:
        match = pattern.search(plan)
        if match:
            # Replace space with nothing to match column names
            data_volume = match.group(1).replace(" ", "")
            # Move the "€" symbol to the front and replace "," with "."
            price = match.group(2).replace(",", ".")
            # Ensure the "€" symbol is moved to the front
            price_formatted = "€" + price[:-1]
            extracted_data[data_volume] = price_formatted
    
    df_plans = pd.DataFrame([extracted_data], index=[search_value])
    
    return df_plans





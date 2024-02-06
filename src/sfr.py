import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def sfr(search_value, file_path):
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
    
    names = soup.find_all(class_="title")
    alt_names = [item.text for item in names if item]
    
    pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
    extracted_texts = [pattern.search(text).group(0) for text in alt_names if pattern.search(text)]
    
    prix_entier = soup.find_all(class_="L")
    prix_decimal = soup.find_all(class_="R")
    alt_prices = [item.text.strip() for item in prix_entier if item]
    alt_decimals = [item.text.strip() for item in prix_decimal if item]
    cleaned_list_decimals = [item for item in alt_decimals if item != '/mois']
    
    plan_prices = {}
    for text, price, decimal in zip(extracted_texts[2:], alt_prices[2:], cleaned_list_decimals[2:]):
        if not decimal:
            decimal_part = ''
        else:
            match = re.search(r"(\d+)", decimal)
            decimal_part = match.group(1) if match else ''
        
        full_price = f"€{price}" + (f".{decimal_part}" if decimal_part else "")
        plan_prices[text.replace(" ", "")] = full_price  # Remove spaces to match column names
    
    df_plans = pd.DataFrame([plan_prices], index=[search_value])
    return df_plans
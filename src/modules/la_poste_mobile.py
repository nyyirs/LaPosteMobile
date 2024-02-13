import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def la_poste_mobile(search_value, file_path):
    """
    Extracts mobile plan details and pricing information based on a given search value.
    
    Parameters:
    - search_value: The name of the mobile plan or provider to search for in the DataFrame.
    - file_path: The path to the excel file to retrieve data from.
    
    Returns:
    - A DataFrame containing the name and price of mobile plans in one row.
    """
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    
    name_col_index = df.columns.get_loc('Name')
    next_col_name = df.columns[name_col_index + 1]
    url = df[df['Name'] == search_value][next_col_name].iloc[0]
    
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to retrieve data"
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    img_tags = soup.find_all(id="imgCaracteristique")
    alt_texts = [img_tag['alt'] for img_tag in img_tags if img_tag]
    formatted_texts = [text.replace('<br/>', '\n') for text in alt_texts]
    
    pattern = re.compile(r"\b\d+(?:Go|Mo)\b")
    extracted_texts = [pattern.search(text).group(0) for text in formatted_texts if pattern.search(text)]
    
    prix_entier = soup.find_all(class_="prix_entier")
    prix_decimal = soup.find_all(class_="decimal")
    alt_prices = [item.text.strip() for item in prix_entier if item]
    alt_decimals = [item.text.strip() for item in prix_decimal if item]
    
    # Initialize an empty dictionary to hold all plan names and prices
    plan_prices = {}
    for text, price, decimal in zip(extracted_texts, alt_prices, alt_decimals):
        if not decimal:
            decimal_part = ''  # Set decimal_part to blank
        else:
            # Extract decimal part using regex if decimal is not blank
            match = re.search(r"(\d+)", decimal)
            decimal_part = match.group(1) if match else ''
        
        # Construct the full price string. Only add the decimal point and part if decimal_part is not blank
        full_price = f"€{price}" + (f".{decimal_part}" if decimal_part else "")
        
        # Add the plan name and price to the dictionary
        plan_prices[text] = full_price
        
    # Create a DataFrame from the dictionary
    df_plans = pd.DataFrame([plan_prices], index=[search_value])
    
    return df_plans
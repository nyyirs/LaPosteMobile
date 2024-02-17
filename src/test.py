# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 20:51:59 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
import os
from dotenv import load_dotenv
import pymssql


# Load environment variables from .env file
load_dotenv()

# Retrieve database connection info from environment variables
server = os.getenv('DB_SERVER')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')  # Formats the current date as YYYY-MM-DD


# Connect to your Azure SQL Database
conn = pymssql.connect(server, username, password, database)

# Create a cursor object
cursor = conn.cursor()

# Execute a SQL query
cursor.execute("SELECT * FROM Operateurs WHERE NomOperateur = 'La Poste Mobile'")

# Fetch the first row
row = cursor.fetchone()

OperateurID, NomOperateur, URLSansEngagement = row

response = requests.get(URLSansEngagement)
soup = BeautifulSoup(response.content, 'html.parser')

names = soup.find_all(id="imgCaracteristique")
alt_names = [names['alt'] for names in names if names]
formatted_names = [text.replace('<br/>', '\n') for text in alt_names]
pattern = re.compile(r"\b\d+(?:Go|Mo)\b")
pattern_5g = re.compile(r"5G")

extracted_names = [pattern.search(text).group(0) for text in formatted_names if pattern.search(text)]
extracted_5g = [bool(pattern_5g.search(text)) for text in formatted_names if text.strip()]

prix_entier = soup.find_all(class_="prix_entier")
prix_decimal = soup.find_all(class_="decimal")
alt_prices = [item.text.strip() for item in prix_entier if item]
alt_decimals = [item.text.strip() for item in prix_decimal if item]

plan_prices = []
for text, price, decimal in zip(extracted_names, alt_prices, alt_decimals):
    if not decimal:
        decimal_part = ''  # Set decimal_part to blank
    else:
        # Extract decimal part using regex if decimal is not blank
        match = re.search(r"(\d+)", decimal)
        decimal_part = match.group(1) if match else ''    
    # Construct the full price string. Only add the decimal point and part if decimal_part is not blank
    full_price = f"€{price}" + (f".{decimal_part}" if decimal_part else "")    
    # Add the plan name and price to the dictionary
    plan_prices.append(full_price)
    
prix_5g = soup.find_all(class_="option5g")
alt_prices_5g = [item.text.strip() for item in prix_5g if item]
extracted_5g_Add = [int(''.join(filter(str.isdigit, item))) if any(c.isdigit() for c in item) else 0 for item in alt_prices_5g]

# Ensure the lengths match, by checking if extracted_5g is longer
if len(extracted_5g) > len(extracted_5g_Add):
    for i in range(len(extracted_5g) - len(extracted_5g_Add)):
        # Check if the corresponding extracted_5g value is False
        if not extracted_5g[len(extracted_5g_Add) + i]:
            extracted_5g_Add.append(0)  # Append 0 if the condition is met
            

forfait_final = []
for index, (name, is_5g, price, price_addon) in enumerate(zip(extracted_names, extracted_5g, plan_prices, extracted_5g_Add)):
    limite, unite = name[:-2], name[-2:]
    compatible5g = 1 if is_5g else 0  # Convert boolean to BIT

    # Convert price to float and calculate new price if 5G is true
    price_float = float(price[1:])  # Remove € and convert to float
    
    #forfait_final.append((index, limite, unite, compatible5g, f"€{price_float:.2f}", date_enregistrement))
    
    # Now insert into Forfaits
    cursor.execute("INSERT INTO Forfaits (OperateurID, LimiteDonnees, UniteDonnees, Compatible5G) VALUES (%s, %s, %s, %s); SELECT SCOPE_IDENTITY();", (OperateurID, limite, unite, 0))
    forfait_id = cursor.fetchone()[0]
    conn.commit()
    
    # Now insert into Tarifs
    sql_query = "INSERT INTO Tarifs (OperateurID, ForfaitID, Prix, DateEnregistrement) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql_query, (OperateurID, int(forfait_id), f"€{price_float:.2f}", date_enregistrement))
    conn.commit()  # Commit the transaction to save the insert         
    
    if is_5g:
        new_price_float = price_float + price_addon
        #forfait_final.append((index, limite, unite, compatible5g, f"€{new_price_float:.2f}", date_enregistrement))
        cursor.execute("INSERT INTO Forfaits (OperateurID, LimiteDonnees, UniteDonnees, Compatible5G) VALUES (%s, %s, %s, %s); SELECT SCOPE_IDENTITY();", (OperateurID, limite, unite, compatible5g))
        forfait_id = cursor.fetchone()[0]
        conn.commit()
        
        # Now insert into Tarifs
        sql_query = "INSERT INTO Tarifs (OperateurID, ForfaitID, Prix, DateEnregistrement) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_query, (OperateurID, int(forfait_id), f"€{new_price_float:.2f}", date_enregistrement))
        conn.commit()  # Commit the transaction to save the insert           
        
    





















            

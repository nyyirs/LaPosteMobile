# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 11:35:12 2024

@author: Nyyir
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
import os
from dotenv import load_dotenv
import pymssql

load_dotenv()

date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')

server = os.getenv('DB_SERVER')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

# Establish connection to the database
conn = pymssql.connect(server=server, user=username, password=password, database=database)

# Create a cursor object using the connection
cursor = conn.cursor()

# Execute the SQL query
cursor.execute("SELECT * FROM Operateurs WHERE NomOperateur = 'SFR'")

# Fetch one record from the query result
operator_data = cursor.fetchone()

OperateurID, NomOperateur, URLSansEngagement = operator_data

response = requests.get(URLSansEngagement)  
        
soup = BeautifulSoup(response.content, 'html.parser')

names = soup.find_all(class_="title")
alt_names = [item.text for item in names if item]

pattern = re.compile(r'\b\d+\s*(Go|Mo)\b')
extracted_texts = [item for item in alt_names if pattern.search(item)]


pattern_5g = re.compile(r"5G")
extracted_5g = [bool(pattern_5g.search(text)) for text in extracted_texts if text.strip()]

prix_entier = soup.find_all(class_="L")
prix_decimal = soup.find_all(class_="R")
alt_prices = [item.text.strip() for item in prix_entier if item]
alt_decimals = [item.text.strip() for item in prix_decimal if item]
cleaned_list_decimals = [item for item in alt_decimals if item != '/mois']

    
plan_prices = []
for text, price, decimal in zip(extracted_texts, alt_prices, cleaned_list_decimals):
    if not decimal:
        decimal_part = ''
    else:
        match = re.search(r"(\d+)", decimal)
        decimal_part = match.group(1) if match else ''
    full_price = f"€{price}" + (f".{decimal_part}" if decimal_part else "")
    plan_prices.append(full_price)

for name, is_5g, price in zip(extracted_texts[2:], extracted_5g[2:], plan_prices[2:]):
    limite, unite = name.split(" ")[0], name.split(" ")[1]
    compatible5g = 1 if is_5g else 0  
    
    if is_5g:        
        #forfait_final.append((index, limite, unite, compatible5g, f"€{new_price_float:.2f}", date_enregistrement))
        cursor.execute("INSERT INTO Forfaits (OperateurID, LimiteDonnees, UniteDonnees, Compatible5G) VALUES (%s, %s, %s, %s); SELECT SCOPE_IDENTITY();", (OperateurID, limite, unite, compatible5g))
        forfait_id = cursor.fetchone()[0]
        conn.commit()
        
        # Now insert into Tarifs
        sql_query = "INSERT INTO Tarifs (OperateurID, ForfaitID, Prix, DateEnregistrement) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_query, (OperateurID, int(forfait_id), price.replace("€", ""), date_enregistrement))
        conn.commit()  # Commit the transaction to save the insert  
        
    else:
        # Now insert into Forfaits
        cursor.execute("INSERT INTO Forfaits (OperateurID, LimiteDonnees, UniteDonnees, Compatible5G) VALUES (%s, %s, %s, %s); SELECT SCOPE_IDENTITY();", (OperateurID, limite, unite, 0))
        forfait_id = cursor.fetchone()[0]
        conn.commit()
        
        # Now insert into Tarifs
        sql_query = "INSERT INTO Tarifs (OperateurID, ForfaitID, Prix, DateEnregistrement) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_query, (OperateurID, int(forfait_id), price.replace("€", ""), date_enregistrement))
        conn.commit()  # Commit the transaction to save the insert             
        
        
conn.close()   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    




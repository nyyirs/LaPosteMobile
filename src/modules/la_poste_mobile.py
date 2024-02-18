import requests
from bs4 import BeautifulSoup
import re
import datetime
from modules.azure_sql_db import load_environment_variables, get_database_connection, fetch_operator_data, insert_into_forfaits, insert_into_tarifs


def parse_plans_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def extract_plan_details(soup):
    names = soup.find_all(id="imgCaracteristique")
    prix_entier = soup.find_all(class_="prix_entier")
    prix_decimal = soup.find_all(class_="decimal")
    prix_5g = soup.find_all(class_="option5g")

    alt_names = [name['alt'] for name in names if name]
    formatted_names = [text.replace('<br/>', '\n') for text in alt_names]
    pattern = re.compile(r"\b\d+(?:Go|Mo)\b")
    pattern_5g = re.compile(r"5G")
    extracted_names = [pattern.search(text).group(0) for text in formatted_names if pattern.search(text)]
    extracted_5g = [bool(pattern_5g.search(text)) for text in formatted_names if text.strip()]

    alt_prices = [item.text.strip() for item in prix_entier if item]
    alt_decimals = [item.text.strip() for item in prix_decimal if item]
    alt_prices_5g = [item.text.strip() for item in prix_5g if item]

    plan_prices = []
    for text, price, decimal in zip(extracted_names, alt_prices, alt_decimals):
        decimal_part = re.search(r"(\d+)", decimal).group(1) if decimal else ''
        full_price = f"€{price}" + (f".{decimal_part}" if decimal_part else "")
        plan_prices.append(full_price)

    extracted_5g_Add = [int(''.join(filter(str.isdigit, item))) if any(c.isdigit() for c in item) else 0 for item in alt_prices_5g]
    if len(extracted_5g) > len(extracted_5g_Add):
        extracted_5g_Add.extend([0] * (len(extracted_5g) - len(extracted_5g_Add)))
        
    return extracted_names, extracted_5g, plan_prices, extracted_5g_Add

def insert_plans_to_database(cursor, conn, operator_data, plan_details, date_enregistrement):
    OperateurID, NomOperateur, URLSansEngagement = operator_data
    extracted_names, extracted_5g, plan_prices, extracted_5g_Add = plan_details

    for name, is_5g, price, price_addon in zip(extracted_names, extracted_5g, plan_prices, extracted_5g_Add):
        limite, unite = name[:-2], name[-2:]
        compatible5g = 1 if is_5g else 0
        price_float = float(price[1:])
        
        forfait_id = insert_into_forfaits(cursor, OperateurID, limite, unite, 0)
        conn.commit()  # Commit the Forfaits insert
        
        insert_into_tarifs(cursor, OperateurID, int(forfait_id),  f"€{price_float:.2f}", date_enregistrement)
        conn.commit() 
        
        if is_5g:
            
            new_price_float = price_float + price_addon
            
            forfait_id = insert_into_forfaits(cursor, OperateurID, limite, unite, compatible5g)
            conn.commit()  # Commit the Forfaits insert
            
            insert_into_tarifs(cursor, OperateurID, int(forfait_id), f"€{new_price_float:.2f}", date_enregistrement)
            conn.commit()            
            

def main():
    load_environment_variables()
    conn = get_database_connection()
    cursor = conn.cursor()

    date_enregistrement = datetime.datetime.now().strftime('%Y-%m-%d')
    operator_data = fetch_operator_data(cursor, 'La Poste Mobile')
    soup = parse_plans_data(operator_data[2])
    plan_details = extract_plan_details(soup)
    insert_plans_to_database(cursor, conn, operator_data, plan_details, date_enregistrement)
    conn.close()

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import re


response = requests.get("https://boutique.orange.fr/mobile/offres?withOpenPrices=false")  

soup = BeautifulSoup(response.content, 'html.parser')

# Extract the plan name
names = soup.find_all(class_="offer-tile")
alt_names = [item.text for item in names if item]
filtered_plan_names = [plan for plan in alt_names if " false " in plan]

pattern = re.compile(r"Forfait \d+h \d+Go|Forfait \d+Go 5G|Forfait \d+h \d+Mo|Forfait \d+Mo|Forfait \d+Go|Série Spéciale \d+Go 5G")
extracted_texts = [re.search(pattern, plan).group(0) if re.search(pattern, plan) else None for plan in filtered_plan_names]

pattern = r'^.*?(\d)'
modified_texts = [re.sub(pattern, r'\1', text) for text in extracted_texts]

# Extract the 5G
pattern_5g = re.compile(r"5G")
extracted_5g = [bool(pattern_5g.search(text)) for text in modified_texts if text.strip()]

#Extract the price
extracted_prices = []
for plan in filtered_plan_names:
    match = re.search(r'(\d+,\d+)€', plan)
    if match:
        price = match.group(1).replace(",", ".")
        extracted_prices.append(f"{price}")










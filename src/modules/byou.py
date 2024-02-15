# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 09:29:32 2024

@author: Nyyir
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from bs4 import BeautifulSoup
import json
import requests

def byou(search_value, file_path):
    """
    Extracts mobile plan details and pricing information based on a given search value.
    
    Parameters:
    - search_value: The name of the mobile plan or provider to search for in the DataFrame.
    - file_path: The path to the excel file to retrieve data from.
    
    Returns:
    - A DataFrame containing the name and price of mobile plans in one row, with plans as columns.
    """    
    #file_path = 'info.xlsx'
    #search_value = 'B&You'
    
    # Setup WebDriver options
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Load the data from the excel file to get the URL
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    name_col_index = df.columns.get_loc('Name')
    next_col_name = df.columns[name_col_index + 1]
    url = df[df['Name'] == search_value][next_col_name].iloc[0]
    
    driver.get(url)
    
    # Accept cookies or close pop-ups if necessary using WebDriver
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='popin_tc_privacy_button_3']"))
        ).click()
    except Exception as e:
        print("No cookie button or specific popup found, or error in clicking:", e)
    
    # Define the plan buttons to click and their corresponding XPaths
    buttons_info = [
        ("10Go", "//*[@id='mainConf']/li[1]/button"),
        ("100Go", "//*[@id='mainConf']/li[2]/button"),
        ("130Go", "//*[@id='mainConf']/li[3]/button"),
        ("200Go", "//*[@id='mainConf']/li[4]/button")
    ]
    
    plan_prices = {}
    
    # Function to click a button and extract the price
    def click_button_and_extract_price(button_xpath):
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        ).click()
    
        price_xpath = "//*[@id='selectedPrice']/div/span[1]"
        decimal_price_xpath = "//*[@id='selectedPrice']/div/span[2]/span[1]"
        price = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, price_xpath))).text.replace(",", ".")
        decimal_price = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, decimal_price_xpath))).text.replace('€', '')
        if decimal_price == "":
            decimal_price = "00"
        price_formatted = f"€{price}.{decimal_price}"
        return price_formatted
    
    # Iterate over each plan, click its button, and extract the price
    for name, xpath in buttons_info:
        plan_prices[name] = click_button_and_extract_price(xpath)
    
    driver.quit()  # Close the WebDriver
    
    # Use requests to get the HTML content again since Selenium driver is closed
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the <script> tag by ID for JSON data extraction
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    # Extract and parse the JSON string
    json_str = script_tag.string if script_tag else '{}'
    data = json.loads(json_str)
    
    data_envelopes_prices = {}
    
    if 'props' in data and 'pageProps' in data['props'] and 'productsList' in data['props']['pageProps'] and 'catalogue' in data['props']['pageProps']['productsList']:
        catalogue = data['props']['pageProps']['productsList']['catalogue']
        for item in catalogue[:3]:
            price = item.get('price')
            data_envelope = item.get('data_envelope')
            if data_envelope and price is not None:
                data_envelopes_prices[data_envelope] = f"€{price}"
    
    # Combine plan_prices with data_envelopes_prices
    combined_data = {**plan_prices, **data_envelopes_prices}
    
    # Create a DataFrame from the combined data
    df_plans = pd.DataFrame([combined_data], index=[search_value])
    
    return df_plans

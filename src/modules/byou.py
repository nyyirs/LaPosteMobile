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

def byou(search_value, file_path):
    """
    Extracts mobile plan details and pricing information based on a given search value.
    
    Parameters:
    - search_value: The name of the mobile plan or provider to search for in the DataFrame.
    - file_path: The path to the excel file to retrieve data from.
    
    Returns:
    - A DataFrame containing the name and price of mobile plans in one row, with plans as columns.
    """    
    #search_value = 'B&You'
    #file_path = 'info.xlsx'
    
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppresses DevTools logs
    
    # Setup WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install(), log_path='NUL'), options=chrome_options)

    # Load the data from the excel file to get the URL
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    name_col_index = df.columns.get_loc('Name')
    next_col_name = df.columns[name_col_index + 1]
    url = df[df['Name'] == search_value][next_col_name].iloc[0]

    # Function to click the button and extract the price
    def click_button_and_extract_price(button_name, button_xpath):
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        ).click()      

        # WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, "//*[@id='content-hp']/main/div[1]/div[4]/ul/li[2]/button"))
        # ).click()

        price_xpath = "//*[@id='selectedPrice']/div/span[1]"
        decimal_price_xpath = "//*[@id='selectedPrice']/div/span[2]/span[1]"

        price = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, price_xpath))).text.replace(",", ".")
        decimal_price = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, decimal_price_xpath))).text

        price_formatted = "€" + price + "." + decimal_price.replace('€','')
        return {button_name: price_formatted}

    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='popin_tc_privacy_button_3']"))
    ).click()

    # Collect initial plan data
    plan_data = {}
    buttons_info = [
        ("10Go", "//*[@id='mainConf']/li[1]/button"),
        ("20Go", "//*[@id='mainConf']/li[2]/button"),
        ("100Go", "//*[@id='mainConf']/li[3]/button"),
        ("200Go", "//*[@id='mainConf']/li[4]/button")
    ]

    for name, xpath in buttons_info:
        plan_data.update(click_button_and_extract_price(name, xpath))

    # Click to expand other forfaits, if needed
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[3]/main/div/div[2]/a'))
    )
    
    # Click the element
    element.click()
    

    # Define XPaths for additional plans and extract their details
    additional_plans = [
        {
            "name_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[1]/div/div[1]/p",
            "price_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[1]/div/div[1]/div/div[1]/span[1]",
            "decimal_price_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[1]/div/div[1]/div/div[1]/span[2]/span[1]"
        },
        {
            "name_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[2]/div/div[1]/p",
            "price_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[2]/div/div[1]/div/div[1]/span[1]",
            "decimal_price_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[2]/div/div[1]/div/div[1]/span[2]/span[1]"
        },
        {
            "name_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[3]/div/div[1]/p",
            "price_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[3]/div/div[1]/p",
            "decimal_price_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[3]/div/div[1]/div/div[1]/span[2]/span[1]"
        },
        {
            "name_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[4]/div/div[1]/p",
            "price_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[4]/div/div[1]/div/div[1]/span[1]",
            "decimal_price_xpath": "/html/body/div[1]/div/div[3]/main/div/div[3]/div[4]/div/div[1]/div/div[1]/span[2]/span[1]"
        }        
    ]

    for plan in additional_plans:
        plan_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, plan["name_xpath"]))).text
        plan_price = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, plan["price_xpath"]))).text.replace(",", ".")
        plan_decimal_price = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, plan["decimal_price_xpath"]))).text
    
        # Remove euro symbol if present and any trailing dots
        plan_price = plan_price.replace("€", "").rstrip('.')
        plan_decimal_price = plan_decimal_price.replace("€", "")
    
        # Format the price correctly
        price_formatted = "€" + plan_price + "." + plan_decimal_price
        plan_data[plan_name] = price_formatted

    # Create the DataFrame from the updated plan_data dictionary
    df_plans = pd.DataFrame([plan_data], index=[search_value])

    driver.quit()
    
    return df_plans




    






















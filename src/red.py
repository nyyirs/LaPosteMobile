# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 09:47:40 2024

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
import time

def red(search_value, file_path):
    """
    Extracts mobile plan details and pricing information based on a given search value.
    
    Parameters:
    - search_value: The name of the mobile plan or provider to search for in the DataFrame.
    - file_path: The path to the excel file to retrieve data from.
    
    Returns:
    - A DataFrame containing the name and price of mobile plans in one row, with plans as columns.
    """

    # search_value = 'RED'
    # file_path = 'info.xlsx'
    
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppresses DevTools logs

    # Setup WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install(), log_path='NUL'), options=chrome_options)
    
    # Load the data from the excel file to get the URL
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    name_col_index = df.columns.get_loc('Name')
    next_col_name = df.columns[name_col_index + 1]
    url = df[df['Name'] == search_value][next_col_name].iloc[0]
    
    driver.get(url)
    
    #Accept Button
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='CkC']/div/div[2]/button[2]"))
    ).click()
    
    plan_data = {}
    buttons_info = [
        ("10Go", "//*[@id='as-cNat']/button[1]"),
        ("100Go", "//*[@id='as-cNat']/button[2]"),
        ("130Go", "//*[@id='as-cNat']/button[3]"),
        ("200Go", "//*[@id='as-cNat']/button[4]")
    ]
    
    for name, xpath in buttons_info:
        plan_data.update(click_button_and_extract_price(driver, name, xpath))
        
    # Convert the plan_data dictionary to DataFrame
    df_plans = pd.DataFrame([plan_data], index=[search_value])
    
    # Make sure to close the WebDriver after the operation to free resources
    driver.quit()    
    
    return df_plans

def click_button_and_extract_price(driver, button_name, button_xpath):
    price_xpath = "//*[@id='alPrice']/div/div/span[1]"
    
    # Correctly capture the initial text using WebDriverWait
    initial_text_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, price_xpath))
    )
    initial_text = initial_text_element.text  # Now you get the text after ensuring the element is present
    
    # Ensure the button is clickable and then click it
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, button_xpath))
    ).click()
    
    # Define a custom wait condition to wait for the text to change
    def text_has_changed(driver, xpath, old_text):
        try:
            return driver.find_element(By.XPATH, xpath).text != old_text
        except:
            return False

    # Now wait for the text at the price_xpath to change from its initial value
    WebDriverWait(driver, 10).until(lambda driver: text_has_changed(driver, price_xpath, initial_text))
    
    # After the text has changed, extract the updated price
    price = driver.find_element(By.XPATH, price_xpath).text.replace(",", ".")
    price_formatted = "€" + price
    return {button_name: price_formatted}

def text_has_changed(driver, xpath, old_text):
    element_text = driver.find_element(By.XPATH, xpath).text
    return element_text != old_text
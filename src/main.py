# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 16:52:49 2024

@author: Nyyir
"""

from flask import Flask, jsonify, send_file
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from decimal import Decimal
import modules.la_poste_mobile as lpm
import modules.sfr as sfr
import modules.orange as orange
import modules.byou as byou
import modules.sosh as sosh
import modules.free as free
import modules.red as red
from modules.azure_sql_db import load_environment_variables, get_database_connection, fetch_all_operator_plan_details

app = Flask(__name__)

# Assuming you have a function to fetch all operator plan details
def create_and_save_excel():
    # Load environment variables
    load_environment_variables()
    
    # Establish database connection
    conn = get_database_connection()
    cursor = conn.cursor()
    
    data_plan = fetch_all_operator_plan_details(cursor)
    
    # Creating DataFrame
    df = pd.DataFrame(data_plan, columns=['CarrierId', 'Carrier', 'Data', 'Unit', 'is5G', 'Price', 'Date'])
    df = df.drop(columns=['CarrierId'])
    # Formatting the 'Price' column by removing trailing zeros
    df['Price'] = df['Price'].apply(lambda x: x.quantize(Decimal('1.')) if x == x.to_integral() else x.normalize())

    # Save to Excel file
    excel_path = 'data_plan.xlsx'
    df.to_excel(excel_path, index=False)

    return excel_path

@app.route('/run-tasks', methods=['GET'])
def run_tasks():
    tasks = [lpm.lpm, sfr.sfr, orange.orange, byou.byou, sosh.sosh, free.free, red.red]
    
    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda task: task(), tasks)
        results_list = list(results)  # Convert results to a list for JSON serialization

    # Create and save the Excel file
    excel_file = create_and_save_excel()

    # Make the file downloadable
    return send_file(excel_file, as_attachment=True, download_name='data_plan.xlsx')

if __name__ == '__main__':
    app.run(debug=True)

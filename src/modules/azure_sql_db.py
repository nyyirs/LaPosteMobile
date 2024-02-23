# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 14:56:18 2024

@author: Nyyir
"""

from dotenv import load_dotenv
import pymssql
import os
import time
import datetime

def load_environment_variables():
    load_dotenv()

def get_database_connection(max_retries=5, delay_seconds=10):
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    
    for attempt in range(1, max_retries + 1):
        try:
            connection = pymssql.connect(server, username, password, database)
            return connection
        except pymssql.OperationalError as e:
            if attempt < max_retries:
                time.sleep(delay_seconds)
            else:
                raise e

def fetch_operator_data(cursor, operator_name):
    cursor.execute("SELECT * FROM Operateurs WHERE NomOperateur = %s", (operator_name,))
    return cursor.fetchone()

def insert_into_forfaits(cursor, OperateurID, limite, unite, compatible5g):
    sql_query = "INSERT INTO Forfaits (OperateurID, LimiteDonnees, UniteDonnees, Compatible5G) VALUES (%s, %s, %s, %s); SELECT SCOPE_IDENTITY();"
    cursor.execute(sql_query, (OperateurID, limite, unite, compatible5g))
    forfait_id = cursor.fetchone()[0]
    return forfait_id

def insert_into_tarifs(cursor, OperateurID, ForfaitID, price, date_enregistrement):
    sql_query = "INSERT INTO Tarifs (OperateurID, ForfaitID, Prix, DateEnregistrement) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql_query, (OperateurID, ForfaitID, price, date_enregistrement))
    
def check_date_exists(cursor):
    # Get today's date in the format 'YYYY-MM-DD'
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # SQL query to check for records with today's date. This gets the count of such records.
    sql_query = "SELECT COUNT(*) FROM Tarifs WHERE DateEnregistrement = %s"
    
    # Execute the query
    cursor.execute(sql_query, (today_date,))
    
    # Fetch the count of records for today's date
    count = cursor.fetchone()[0]
    
    # If count is greater than 0, then at least one record exists for today's date
    return count > 0

def fetch_all_operator_plan_details(cursor):
    sql_query = """
        SELECT 
            o.OperateurID,
            o.NomOperateur, 
            f.LimiteDonnees, 
            f.UniteDonnees, 
            f.Compatible5G, 
            t.Prix, 
            t.DateEnregistrement
        FROM Operateurs o
        INNER JOIN Forfaits f ON o.OperateurID = f.OperateurID
        INNER JOIN Tarifs t ON f.ForfaitID = t.ForfaitID
        AND o.OperateurID = t.OperateurID
        ORDER BY OperateurID;
        """
    cursor.execute(sql_query)
    return cursor.fetchall()
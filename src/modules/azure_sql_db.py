# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 14:56:18 2024

@author: Nyyir
"""

from dotenv import load_dotenv
import pymssql
import os

def load_environment_variables():
    load_dotenv()

def get_database_connection():
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_NAME')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    return pymssql.connect(server, username, password, database)

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


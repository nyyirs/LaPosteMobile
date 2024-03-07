from dotenv import load_dotenv
import pymssql
import os
import logging
import datetime
import time

class DatabaseConnectionError(Exception):
    pass

class DatabaseUtility:
    def __init__(self):
        load_dotenv()
        self.server = os.getenv('DB_SERVER')
        self.database = os.getenv('DB_NAME')
        self.username = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.conn = None
        self._connect()

    def _connect(self, max_retries=5, delay_seconds=10):
        for attempt in range(max_retries):
            try:
                self.conn = pymssql.connect(self.server, self.username, self.password, self.database)
                return
            except pymssql.OperationalError as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise DatabaseConnectionError("Failed to connect to database after several attempts.") from e
                time.sleep(delay_seconds)

    def execute_query(self, query, params=None, fetchone=False):
        with self.conn.cursor(as_dict=True) as cursor:
            cursor.execute(query, params)
            if fetchone:
                return cursor.fetchone()
            return cursor.fetchall()

    def insert_and_return_id(self, query, params):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            cursor_id = cursor.fetchone()[0]
            self.conn.commit()
            return cursor_id

    def execute_non_query(self, query, params):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            self.conn.commit()

# Example usage of DatabaseUtility class for specific operations
class OperatorDatabaseOperations:
    def __init__(self):
        self.db_util = DatabaseUtility()

    def fetch_operator_data(self, operator_name):
        query = "SELECT * FROM Operateurs WHERE NomOperateur = %s"
        return self.db_util.execute_query(query, (operator_name,), fetchone=True)

    def insert_into_forfaits(self, OperateurID, limite, unite, compatible5g, adsl, fibre, avecEngagement, annee):
        query = """
        INSERT INTO Forfaits (OperateurID, LimiteDonnees, UniteDonnees, Compatible5G, Adsl, Fibre, AvecEngagement, Annee)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s); SELECT SCOPE_IDENTITY();
        """
        return self.db_util.insert_and_return_id(query, (OperateurID, limite, unite, compatible5g, adsl, fibre, avecEngagement, annee))

    def insert_into_tarifs(self, ForfaitID, price, date_enregistrement):
        query = """
        INSERT INTO Tarifs (ForfaitID, Prix, DateEnregistrement)
        VALUES (%s, %s, %s)
        """
        self.db_util.execute_non_query(query, (ForfaitID, price, date_enregistrement))

    def check_date_exists(self):
        today_date = datetime.datetime.now().strftime('%Y-%m-%d')
        query = "SELECT COUNT(*) FROM Tarifs WHERE DateEnregistrement = %s"
        result = self.db_util.execute_query(query, (today_date,), fetchone=True)
        return result[''] > 0

    def fetch_all_operator_plan_details(self):
        query = """
        SELECT 
            o.OperateurID, o.NomOperateur, f.LimiteDonnees, f.UniteDonnees, 
            f.Compatible5G, t.Prix, t.DateEnregistrement
        FROM Operateurs o
        INNER JOIN ForfaitsSansEngagement f ON o.OperateurID = f.OperateurID
        INNER JOIN TarifsSansEngagement t ON f.ForfaitID = t.ForfaitID
        AND o.OperateurID = t.OperateurID
        ORDER BY OperateurID;
        """
        return self.db_util.execute_query(query)

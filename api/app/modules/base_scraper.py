import logging
from azure_database_utils import OperatorDatabaseOperations

class BaseScraper:
    def __init__(self, operator_name):
        self.operator_name = operator_name
        self.db_operations = OperatorDatabaseOperations()
        self.operator_data = None

    def setup(self):
        """Prepare scraper by fetching operator details."""
        self.operator_data = self.db_operations.fetch_operator_data(self.operator_name)
        if not self.operator_data:
            logging.error(f"No data found for operator: {self.operator_name}")
            raise ValueError("Operator data not found.")

    def scrape_data(self):
        """Scrape data from the operator's website."""
        raise NotImplementedError("Subclass must implement the scrape_data method.")

    def process_data(self):
        """Process scraped data."""
        raise NotImplementedError("Subclass must implement the process_data method.")

    def insert_data(self):
        """Insert processed data into the database."""
        raise NotImplementedError("Subclass must implement the insert_data method.")

    def run(self):
        """Execute the scraper workflow."""
        try:
            self.setup()
            self.scrape_data()
            self.process_data()
            self.insert_data()
            logging.info(f"Successfully completed scraping and processing for {self.operator_name}")
        except Exception as e:
            logging.error(f"An error occurred while running the scraper for {self.operator_name}: {e}")

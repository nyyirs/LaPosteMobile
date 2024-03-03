import logging
from datetime import datetime

class ErrorCounterHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self.error_count = 0

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.error_count += 1

class ExcludeSpecificLogFilter(logging.Filter):
    def __init__(self, substring):
        super().__init__()
        self.substring = substring

    def filter(self, record):
        # Return False if the specified substring is found in the message, True otherwise
        return self.substring not in record.getMessage()            

def configure_logging():
    
    error_counter_handler = ErrorCounterHandler()

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Generate log file name with the current date
    current_date = datetime.now().strftime("%Y_%m_%d")
    log_file_name = f"{current_date}.log"

    # Create a file handler for logging to a file
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d')
    file_handler.setFormatter(formatter)

    # Optionally, create a console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add a filter to exclude specific log messages
    exclude_filter = ExcludeSpecificLogFilter("https://stlpmprod.blob.core.windows.net")
    file_handler.addFilter(exclude_filter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)  # Comment or remove if console output is not needed
    logger.addHandler(file_handler)
    logger.addHandler(error_counter_handler)

    return error_counter_handler, file_handler

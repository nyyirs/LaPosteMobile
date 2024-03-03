# Import FastAPI
from fastapi import FastAPI
import logging
from modules.logging_config import configure_logging

from modules.auchantelecom import Auchan
from modules.byou import Byou
from modules.coriolis import Coriolis
from modules.creditmutuel import Creditmutuel
from modules.free import Free
from modules.cdiscount import Cdiscount
from modules.lapostemobile import Lapostemobile
from modules.lebara import Lebara
from modules.lyca import Lyca
from modules.nrj import Nrj
from modules.orange import Orange
from modules.prixtel import Prixtel
from modules.reglo import Reglo
from modules.sfr import Sfr
from modules.red import Red
from modules.sosh import Sosh
from modules.syma import Syma
from modules.youprice import Youprice
from modules.azure_blob_uploader import AzureBlobUploader

# Create an instance of the FastAPI class
app = FastAPI()

# Configure logging and get the custom error counter handler
error_counter_handler, file_handler = configure_logging()

# Your application code here
logger = logging.getLogger(__name__)

# Define a root `/` endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to La Poste Mobile Scraping Tool"}

@app.get("/run")
async def run():
    scrapers = [Auchan(), Byou(), Coriolis(), Creditmutuel(), Free(), Cdiscount(), Lapostemobile(),
        Lebara(), Lyca(), Nrj(), Orange(), Prixtel(), Reglo(), Sfr(), Red(),
        Sosh(), Syma(), Youprice()]    
    for scraper in scrapers:
        logging.info("------------------------Start-----------------------")
        scraper.run()
        logging.info("------------------------End-------------------------\n")    
    logging.info(f"Total Errors Logged: {error_counter_handler.error_count} \n")
    return {"message": "Scraping completed", "errors": error_counter_handler.error_count}

@app.get("/upload")
async def upload():
    global file_handler  # Assuming file_handler is made global for access here
    uploader = AzureBlobUploader()
    # Close the file handler to release the log file before deleting it
    if file_handler:
        logging.getLogger().removeHandler(file_handler)
        file_handler.close()
    uploader.upload_log_file()  
    return {"message": "Upload completed"}


    
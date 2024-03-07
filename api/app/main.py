from fastapi import FastAPI
import logging
from modules.logging_config import configure_logging

from modules.forfaits_sans_engagement.auchantelecom import Auchan
from modules.forfaits_sans_engagement.byou import Byou
from modules.forfaits_sans_engagement.coriolis import Coriolis
from modules.forfaits_sans_engagement.creditmutuel import Creditmutuel
from modules.forfaits_sans_engagement.free import Free
from modules.forfaits_sans_engagement.cdiscount import Cdiscount
from modules.forfaits_sans_engagement.lapostemobile import Lapostemobile
from modules.forfaits_sans_engagement.lebara import Lebara
from modules.forfaits_sans_engagement.lyca import Lyca
from modules.forfaits_sans_engagement.nrj import Nrj
from modules.forfaits_sans_engagement.orange import Orange
from modules.forfaits_sans_engagement.prixtel import Prixtel
from modules.forfaits_sans_engagement.reglo import Reglo
from modules.forfaits_sans_engagement.sfr import Sfr
from modules.forfaits_sans_engagement.red import Red
from modules.forfaits_sans_engagement.sosh import Sosh
from modules.forfaits_sans_engagement.syma import Syma
from modules.forfaits_sans_engagement.youprice import Youprice
from modules.azure_blob_uploader import AzureBlobUploader

app = FastAPI()

# Your application code here
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    return {"message": "Welcome to La Poste Mobile Scraping Tool"}

@app.get("/run")
async def run():
    # Configure logging and get the custom error counter handler
    # This ensures logging starts here
    error_counter_handler, file_handler = configure_logging()
    scrapers = [
        Auchan(), Byou(), Coriolis(), Creditmutuel(), Free(), Cdiscount(), Lapostemobile(),
        Lebara(), Lyca(), Nrj(), Orange(), Prixtel(), Reglo(), Sfr(), Red(),
        Sosh(), Syma(), Youprice()
    ] 
    for scraper in scrapers:
        logging.info("------------------------Start-----------------------")
        scraper.run()
        logging.info("------------------------End-------------------------\n")    
    logging.info(f"Total Errors Logged: {error_counter_handler.error_count} \n")

    uploader = AzureBlobUploader()
    # Close the file handler to release the log file before deleting it
    if file_handler:
        logging.getLogger().removeHandler(file_handler)
        file_handler.close()
    uploader.upload_log_file()  

    return {"message": "Scraping completed", "errors": error_counter_handler.error_count}

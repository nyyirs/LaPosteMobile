# Import FastAPI
from fastapi import FastAPI
import logging
from modules.logging_config import configure_logging
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

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

# Create an instance of the FastAPI class
app = FastAPI()

# Configure logging and get the custom error counter handler
error_counter_handler = configure_logging()

# Your application code here
logger = logging.getLogger(__name__)

# Define a root `/` endpoint
@app.get("/")
async def read_root():
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

    return {"message": "Scraping completed",}

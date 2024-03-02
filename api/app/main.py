# Import FastAPI
from fastapi import FastAPI
import logging
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

# Configure logging at the start of your application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a root `/` endpoint
@app.get("/")
async def read_root():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scrapers = [
        Auchan(), Byou(), Coriolis(), Creditmutuel(), Free(), Cdiscount(), Lapostemobile(),
        Lebara(), Lyca(), Nrj(), Orange(), Prixtel(), Reglo(), Sfr(), Red(),
        Sosh(), Syma(), Youprice()
    ]    
    for scraper in scrapers:
        logging.info("\n ---------------------------------------------------------")
        scraper.run()
        
    return {"message": "Scraping completed successfully"}

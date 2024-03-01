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

# Define a root `/` endpoint
@app.get("/")
async def read_root():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    scrapers = [
        Auchan(), Byou(), Coriolis(), Creditmutuel(), Free(), Cdiscount(), Lapostemobile(),
        Lebara(), Lyca(), Nrj(), Orange(), Prixtel(), Reglo(), Sfr(), Red(),
        Sosh(), Syma(), Youprice()
    ]    
    # Use ThreadPoolExecutor to run scrapers in parallel
    with ThreadPoolExecutor() as executor:
        future_to_scraper = {executor.submit(scraper.run): scraper for scraper in scrapers}
        for future in concurrent.futures.as_completed(future_to_scraper):
            scraper = future_to_scraper[future]
            try:
                data = future.result()
            except Exception as exc:
                return {"message": "Error found during scraping"}
    return {"message": "Scraping completed successfully"}

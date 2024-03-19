from fastapi import FastAPI
import logging
from modules.logging_config import configure_logging

from modules.forfaits_sans_engagement.auchantelecom import Auchan as AuchanSansEngagement
from modules.forfaits_sans_engagement.byou import Byou as ByouSansEngagement
from modules.forfaits_sans_engagement.coriolis import Coriolis as CoriolisSansEngagement
from modules.forfaits_sans_engagement.creditmutuel import Creditmutuel as CreditmutuelSansEngagement
from modules.forfaits_sans_engagement.free import Free as FreeSansEngagement
from modules.forfaits_sans_engagement.cdiscount import Cdiscount as CdiscountSansEngagement
from modules.forfaits_sans_engagement.lapostemobile import Lapostemobile as LapostemobileSansEngagement
from modules.forfaits_sans_engagement.lebara import Lebara as LebaraSansEngagement
from modules.forfaits_sans_engagement.lyca import Lyca as LycaSansEngagement
from modules.forfaits_sans_engagement.nrj import Nrj as NrjSansEngagement
from modules.forfaits_sans_engagement.orange import Orange as OrangeSansEngagement
from modules.forfaits_sans_engagement.prixtel import Prixtel as PrixtelSansEngagement
from modules.forfaits_sans_engagement.reglo import Reglo as RegloSansEngagement
from modules.forfaits_sans_engagement.sfr import Sfr as SfrSansEngagement
from modules.forfaits_sans_engagement.red import Red as RedSansEngagement
from modules.forfaits_sans_engagement.sosh import Sosh as SoshSansEngagement
from modules.forfaits_sans_engagement.syma import Syma as SymaSansEngagement
from modules.forfaits_sans_engagement.youprice import Youprice as YoupriceSansEngagement

from modules.forfaits_avec_engagement.byou import Byou as ByouAvecEngagement
from modules.forfaits_avec_engagement.lapostemobile import Lapostemobile as LapostemobileAvecEngagement
from modules.forfaits_avec_engagement.orange import Orange as OrangeAvecEngagement
from modules.forfaits_avec_engagement.sfr import Sfr as SfrAvecEngagement

from modules.fixe.byou import Byou as ByouFixe
from modules.fixe.free import Free as FreeFixe
from modules.fixe.orange import Orange as OrangeFixe
from modules.fixe.sfr import Sfr as SfrFixe
from modules.fixe.red import Red as RedFixe
from modules.fixe.sosh import Sosh as SoshFixe

from modules.deja_client.byou import Byou as ByouDejaClient
from modules.deja_client.free import Free as FreeDejaClient
from modules.deja_client.orange import Orange as OrangeDejaClient
from modules.deja_client.sfr import Sfr as SfrDejaClient
from modules.deja_client.lapostemobile import Lapostemobile as LapostemobileDejaClient


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
    error_counter_handler, file_handler = configure_logging()
    scrapers_sans_engagement = [
        AuchanSansEngagement(), ByouSansEngagement(), CoriolisSansEngagement(),
        CreditmutuelSansEngagement(), FreeSansEngagement(), CdiscountSansEngagement(),
        LapostemobileSansEngagement(), LebaraSansEngagement(), LycaSansEngagement(),
        NrjSansEngagement(), OrangeSansEngagement(), PrixtelSansEngagement(),
        RegloSansEngagement(), SfrSansEngagement(), RedSansEngagement(),
        SoshSansEngagement(), SymaSansEngagement(), YoupriceSansEngagement()
    ]
    scrapers_avec_engagement = [
        ByouAvecEngagement(), LapostemobileAvecEngagement(),
        OrangeAvecEngagement(), SfrAvecEngagement()
    ]
    scrapers_fixe = [
        ByouFixe(), FreeFixe(), RedFixe(), SoshFixe(), OrangeFixe(), SfrFixe()
    ]
    scrapers_deja_client = [
        ByouDejaClient(), FreeDejaClient(), LapostemobileDejaClient(), OrangeDejaClient(), SfrDejaClient()
    ]
    # Run sans engagement scrapers
    run_scrapers(scrapers_sans_engagement)    
    # Run avec engagement scrapers
    run_scrapers(scrapers_avec_engagement)
    # Run Fixe scrapers
    run_scrapers(scrapers_fixe)
    run_scrapers(scrapers_deja_client) 
    # Log total errors and upload the log file
    logging.info(f"Total Errors Logged: {error_counter_handler.error_count}\n")    
    uploader = AzureBlobUploader()
    # Close the file handler to release the log file before deleting it
    if file_handler:
        logging.getLogger().removeHandler(file_handler)
        file_handler.close()
    uploader.upload_log_file()
    return {"message": "Scraping completed", "errors": error_counter_handler.error_count}

def run_scrapers(scraper_list):
    for scraper in scraper_list:
        logging.info("------------------------Start-----------------------")
        scraper.run()
        logging.info("------------------------End-------------------------\n")
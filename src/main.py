# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 16:52:49 2024

@author: Nyyir
"""

# Import the entire module
import modules.la_poste_mobile as lpm
import modules.sfr as sfr
import modules.orange as orange
import modules.byou as byou
import modules.sosh as sosh
import modules.free as free
from concurrent.futures import ThreadPoolExecutor

def run():
    # List of functions to execute
    tasks = [lpm.lpm, sfr.sfr, orange.orange, byou.byou, sosh.soch, free.free]

    # Use ThreadPoolExecutor to execute multiple tasks concurrently
    with ThreadPoolExecutor() as executor:
        # Map each function to the executor
        # The executor.map function returns results in the order the functions were started
        results = executor.map(lambda task: task(), tasks)
        
        # Optional: Iterate through results if you need to process them
        # for result in results:
        #     process(result)

if __name__ == "__main__":
    run()

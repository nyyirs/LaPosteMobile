# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 16:52:49 2024

@author: Nyyir
"""

# Import the entire module
import modules.la_poste_mobile as lpm
import modules.sfr as sfr
import modules.orange as orange

def run():

    lpm.lpm()
    sfr.sfr()
    orange.orange()

if __name__ == "__main__":
    run()
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 16:52:49 2024

@author: Nyyir
"""

from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor
import modules.la_poste_mobile as lpm
import modules.sfr as sfr
import modules.orange as orange
import modules.byou as byou
import modules.sosh as sosh
import modules.free as free

app = Flask(__name__)

@app.route('/run-tasks', methods=['GET'])
def run_tasks():
    tasks = [lpm.lpm, sfr.sfr, orange.orange, byou.byou, sosh.sosh, free.free]
    
    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda task: task(), tasks)
        results_list = list(results) # Convert results to a list for JSON serialization

    return jsonify({"results": results_list})

if __name__ == '__main__':
    app.run(debug=True)

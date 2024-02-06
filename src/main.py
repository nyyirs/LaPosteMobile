# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 16:31:25 2024

@author: Nyyir
"""

# main.py

from la_poste_mobile import la_poste_mobile
from sfr import sfr
import pandas as pd

def main():
    
    df_la_poste = la_poste_mobile('La Poste Mobile', 'info.xlsx')
    df_sfr = sfr('SFR', 'info.xlsx')
    
    # Merge the DataFrames
    merged_df = pd.concat([df_la_poste, df_sfr], axis=0)
    
    # Fill NaN values with an empty string to display blank where there is no price
    merged_df.fillna('', inplace=True)
    
    # Export to Excel with column headers in bold
    with pd.ExcelWriter('Results.xlsx', engine='xlsxwriter') as writer:
        merged_df.to_excel(writer, sheet_name='Plans', index=True)
        
        workbook = writer.book
        worksheet = writer.sheets['Plans']
        
        # Add a format for bold text
        bold_format = workbook.add_format({'bold': True})
        
        # Apply the format to the column headers
        for col_num, value in enumerate(merged_df.columns.values):
            worksheet.write(0, col_num + 1, value, bold_format)  # +1 because of the index column
    
        # Optionally, you can also set the index (provider names) to bold
        for row_num, value in enumerate(merged_df.index.values, start=1):  # start=1 to skip header row
            worksheet.write(row_num, 0, value, bold_format)

if __name__ == "__main__":
    main()

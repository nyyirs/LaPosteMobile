# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 16:31:25 2024

@author: Nyyir
"""

# main.py

from modules import la_poste_mobile, sfr, orange, byou, sosh, red, free, nrj
import pandas as pd

def convert_to_mb(column_name):
    """
    Convert column names to a uniform unit (megabytes) for comparison.
    """
    try:
        value, unit = float(column_name[:-2]), column_name[-2:]
        if unit == 'Go':
            return value * 1024  # Convert gigabytes to megabytes
        elif unit == 'Mo':
            return value
    except ValueError:
        # Handle cases where the column name does not end with 'Go' or 'Mo'
        return 0
    return 0

def main():
    # Assume these functions return DataFrames as per your setup
    df_la_poste = la_poste_mobile.la_poste_mobile('La Poste Mobile', 'info.xlsx')
    df_sfr = sfr.sfr('SFR', 'info.xlsx')
    df_orange = orange.orange('Orange', 'info.xlsx')
    df_byou = byou.byou('B&You', 'info.xlsx')
    df_sosh = sosh.sosh('Sosh', 'info.xlsx')
    df_red = red.red('RED', 'info.xlsx')
    df_free = free.free('Free', 'info.xlsx')
    df_nrj = nrj.nrj('NRJ Mobile', 'info.xlsx')
    
    # Merge the DataFrames
    merged_df = pd.concat([df_la_poste, df_sfr, df_orange, df_byou, df_sosh, df_red, df_free, df_nrj], axis=0)
    
    # Convert column names for sorting
    mb_values = {col: convert_to_mb(col) for col in merged_df.columns}
    
    # Sort columns based on their MB values, ignoring non-data columns
    sorted_columns = [col for col in sorted(mb_values, key=mb_values.get) if mb_values[col] > 0]
    non_data_columns = [col for col in merged_df.columns if mb_values[col] == 0]
    sorted_columns = non_data_columns + sorted_columns  # Keep non-data columns (if any) in their original order
    
    # Reorder DataFrame columns based on sorted column names
    merged_df = merged_df[sorted_columns]
    
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
    
        # Optionally, set the index (provider names) to bold
        for row_num, value in enumerate(merged_df.index.values, start=1):  # start=1 to skip header row
            worksheet.write(row_num, 0, value, bold_format)

if __name__ == "__main__":
    main()


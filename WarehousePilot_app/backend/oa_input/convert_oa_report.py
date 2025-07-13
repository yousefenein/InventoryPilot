#!/usr/bin/env python3

"""
Script to convert OA report formats to ensure compatibility with WarehousePilot backend.
This adds required columns that might be missing from the source file.
"""

import pandas as pd
import os
import sys

def convert_oa_report(input_path, output_path=None):
    """
    Convert OA report file to a format compatible with the WarehousePilot backend.
    
    Args:
        input_path: Path to the input OA report file
        output_path: Path to save the output file (default: same directory with "_converted" suffix)
    """
    # Determine file extension
    file_extension = os.path.splitext(input_path)[1].lower()
    
    # Read the file
    if file_extension in ['.xlsx', '.xlsm']:
        df = pd.read_excel(input_path, engine='openpyxl')
    elif file_extension == '.csv':
        df = pd.read_csv(input_path)
    else:
        print(f"Unsupported file format: {file_extension}")
        return False
    
    # Check for columns and add if missing
    required_columns = [
        '275',         # material_type
        'NoCommande',  # order_id
        'QteAProd',    # qty
        'NoProd',      # sku_color
        'Departement', # department
        'LineUpNo',    # lineup_nb
        'LineupName',  # lineup_name
        'MaxDate',     # due_date
        'NomClientLiv',# client_name
        'ProjectType', # project_type
        'LOC',         # location
        'AREA',        # area
        'MODEL FINAL', # final_model
        'StatutOA',    # importance
    ]
    
    # Add missing columns with empty values
    for column in required_columns:
        if column not in df.columns:
            if column == '275':
                # Try to derive material type from Departement if possible
                if 'Departement' in df.columns:
                    df[column] = df['Departement'].apply(lambda x: x.split()[0] if isinstance(x, str) and ' ' in x else '')
                else:
                    df[column] = ''
            elif column == 'LOC':
                df[column] = ''
            elif column == 'AREA':
                df[column] = ''
            elif column == 'MODEL FINAL':
                df[column] = ''
            else:
                df[column] = ''
            print(f"Added missing column: {column}")
    
    # Determine output path if not provided
    if output_path is None:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_converted{file_extension}"
    
    # Save the converted file
    if file_extension in ['.xlsx', '.xlsm']:
        df.to_excel(output_path, index=False, engine='openpyxl')
    else:  # csv
        df.to_csv(output_path, index=False)
    
    print(f"Converted file saved to: {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_oa_report.py <input_file> [output_file]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_path):
        print(f"Error: Input file does not exist: {input_path}")
        sys.exit(1)
    
    success = convert_oa_report(input_path, output_path)
    if not success:
        sys.exit(1)

"""
Export functionality for MapLeads
Handles exporting data to various formats
"""

import json
import pandas as pd
from typing import List, Dict
from pathlib import Path

def export_businesses(businesses: List[Dict], output_path: str, format: str):
    """Export businesses to specified format"""
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(businesses)
    
    # Clean up data for export
    if 'metadata' in df.columns:
        # Extract useful info from metadata if present
        df.drop('metadata', axis=1, inplace=True)
    
    # Ensure path
    output_path = Path(output_path)
    
    if format == 'csv':
        df.to_csv(output_path, index=False)
    
    elif format == 'json':
        df.to_json(output_path, orient='records', indent=2)
    
    elif format == 'xlsx':
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Businesses', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Businesses']
            for column in df:
                column_width = max(df[column].astype(str).map(len).max(), len(column))
                col_idx = df.columns.get_loc(column)
                worksheet.column_dimensions[chr(65 + col_idx)].width = min(column_width + 2, 50)
    
    else:
        raise ValueError(f"Unsupported format: {format}")

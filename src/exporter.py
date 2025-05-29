"""
Export functionality for MapLeads
Handles exporting data to various formats
"""

import json
import pandas as pd
from typing import List, Dict, Tuple
from pathlib import Path
from datetime import datetime

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

def import_businesses(input_path: str) -> Tuple[List[Dict], List[str]]:
    """Import businesses from file and return (businesses, validation_errors)"""
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Import file not found: {input_path}")
    
    # Determine format from extension
    extension = input_path.suffix.lower()
    
    if extension == '.csv':
        df = pd.read_csv(input_path)
    elif extension == '.json':
        with open(input_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    elif extension == '.xlsx':
        df = pd.read_excel(input_path)
    else:
        raise ValueError(f"Unsupported import format: {extension}")
    
    # Convert to list of dictionaries
    businesses = df.to_dict('records')
    
    # Validate and clean the data
    validated_businesses, errors = validate_import_data(businesses)
    
    return validated_businesses, errors

def validate_import_data(businesses: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """Validate imported business data and return (valid_businesses, errors)"""
    required_fields = ['name', 'phone', 'category']
    optional_fields = ['reviews', 'rating', 'website', 'city', 'state', 'zip_code', 'latitude', 'longitude']
    
    valid_businesses = []
    errors = []
    
    for i, business in enumerate(businesses):
        row_errors = []
        
        # Check required fields
        for field in required_fields:
            if field not in business or not business[field] or pd.isna(business[field]):
                row_errors.append(f"Missing required field: {field}")
        
        # Validate phone number format
        if 'phone' in business and business['phone']:
            phone = str(business['phone']).strip()
            # Remove formatting characters
            clean_phone = ''.join(filter(str.isdigit, phone))
            if len(clean_phone) != 10:
                row_errors.append(f"Invalid phone number format: {phone}")
            else:
                business['phone'] = clean_phone
        
        # Validate rating if present
        if 'rating' in business and business['rating'] and not pd.isna(business['rating']):
            try:
                rating = float(business['rating'])
                if not (0 <= rating <= 5):
                    row_errors.append(f"Rating must be between 0-5: {rating}")
                else:
                    business['rating'] = rating
            except (ValueError, TypeError):
                row_errors.append(f"Invalid rating format: {business['rating']}")
                business['rating'] = None
        
        # Clean string fields
        for field in ['name', 'category', 'city', 'state']:
            if field in business and business[field] and not pd.isna(business[field]):
                business[field] = str(business[field]).strip()
        
        # Set default values for missing optional fields
        for field in optional_fields:
            if field not in business or pd.isna(business[field]):
                business[field] = None
        
        # Add metadata
        business['imported_at'] = datetime.now().isoformat()
        business['source'] = 'import'
        
        if row_errors:
            errors.append(f"Row {i+1}: {'; '.join(row_errors)}")
        else:
            valid_businesses.append(business)
    
    return valid_businesses, errors

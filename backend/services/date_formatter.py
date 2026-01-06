"""
Date Format Converter for KYRON
Handles conversion between different date formats for form filling
"""

from datetime import datetime
from typing import Optional
import re

class DateFormatter:
    """Utility class for date format conversion"""
    
    @staticmethod
    def convert_to_dd_mm_yyyy(date_str: str) -> Optional[str]:
        """
        Convert date from various formats to DD/MM/YYYY
        
        Args:
            date_str: Date string in various formats (YYYY-MM-DD, DD-MM-YYYY, etc.)
            
        Returns:
            Date string in DD/MM/YYYY format or None if invalid
        """
        if not date_str:
            return None
        
        # Remove whitespace
        date_str = date_str.strip()
        
        # Try parsing different formats
        formats_to_try = [
            ("%Y-%m-%d", "%d/%m/%Y"),  # 2005-08-25 -> 25/08/2005
            ("%Y/%m/%d", "%d/%m/%Y"),  # 2005/08/25 -> 25/08/2005
            ("%d-%m-%Y", "%d/%m/%Y"),  # 25-08-2005 -> 25/08/2005
            ("%d/%m/%Y", "%d/%m/%Y"),  # Already in correct format
            ("%m/%d/%Y", "%d/%m/%Y"),  # US format -> DD/MM/YYYY
            ("%d.%m.%Y", "%d/%m/%Y"),  # 25.08.2005 -> 25/08/2005
        ]
        
        for input_format, output_format in formats_to_try:
            try:
                date_obj = datetime.strptime(date_str, input_format)
                return date_obj.strftime(output_format)
            except ValueError:
                continue
        
        # Try regex-based parsing for non-standard formats
        # Match YYYY-MM-DD pattern
        yyyy_mm_dd_pattern = r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})'
        match = re.match(yyyy_mm_dd_pattern, date_str)
        if match:
            year, month, day = match.groups()
            try:
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime("%d/%m/%Y")
            except ValueError:
                pass
        
        # Match DD-MM-YYYY pattern
        dd_mm_yyyy_pattern = r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})'
        match = re.match(dd_mm_yyyy_pattern, date_str)
        if match:
            day, month, year = match.groups()
            try:
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime("%d/%m/%Y")
            except ValueError:
                pass
        
        return None
    
    @staticmethod
    def is_date_field(field_name: str, field_label: str = "") -> bool:
        """
        Check if a field is likely a date field
        
        Args:
            field_name: Field name/id
            field_label: Field label text
            
        Returns:
            True if field appears to be a date field
        """
        date_keywords = [
            'dob', 'date', 'birth', 'birthday', 'birth_date', 'date_of_birth',
            'dob', 'd.o.b', 'birthdate', 'birth_date', 'date of birth'
        ]
        
        combined_text = f"{field_name} {field_label}".lower()
        
        for keyword in date_keywords:
            if keyword in combined_text:
                return True
        
        return False
    
    @staticmethod
    def format_for_field(value: str, field_name: str = "", field_label: str = "", field_type: str = "") -> str:
        """
        Format value based on field type and name
        
        Args:
            value: Original value
            field_name: Field name/id
            field_label: Field label
            field_type: HTML field type
            
        Returns:
            Formatted value
        """
        # Check if it's a date field
        if DateFormatter.is_date_field(field_name, field_label) or field_type == "date":
            formatted = DateFormatter.convert_to_dd_mm_yyyy(value)
            if formatted:
                return formatted
        
        # Return original value if not a date or conversion failed
        return value


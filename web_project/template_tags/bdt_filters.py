"""
Custom template filters for BDT (Bangladeshi Taka) formatting
Implements South Asian numbering system with proper comma placement
"""

from django import template
from decimal import Decimal, InvalidOperation
import re

register = template.Library()

@register.filter
def bdt_format(value):
    """
    Format numbers in BDT (Bangladeshi Taka) style with South Asian comma placement
    
    Examples:
    - 1000 -> 1,000
    - 10000 -> 10,000  
    - 100000 -> 1,00,000
    - 1000000 -> 10,00,000
    - 10000000 -> 1,00,00,000
    
    Args:
        value: Number to format (int, float, Decimal, or string)
        
    Returns:
        Formatted string with BDT-style comma placement
    """
    if value is None or value == '':
        return '0'
    
    try:
        # Convert to Decimal for precise handling
        if isinstance(value, str):
            # Remove any existing commas and whitespace
            clean_value = re.sub(r'[,\s]', '', value)
            num = Decimal(clean_value)
        else:
            num = Decimal(str(value))
        
        # Handle negative numbers
        is_negative = num < 0
        num = abs(num)
        
        # Split into integer and decimal parts
        parts = str(num).split('.')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 and parts[1] != '0' else None
        
        # Apply BDT formatting to integer part
        formatted_integer = _format_bdt_integer(integer_part)
        
        # Combine parts
        result = formatted_integer
        if decimal_part:
            result += '.' + decimal_part
        
        # Add negative sign if needed
        if is_negative:
            result = '-' + result
            
        return result
        
    except (InvalidOperation, ValueError, TypeError):
        return str(value)

def _format_bdt_integer(integer_str):
    """
    Apply BDT-style comma formatting to integer part
    
    BDT formatting rules:
    - First comma after 3 digits from right (thousands)
    - Subsequent commas after every 2 digits (lakhs, crores)
    
    Args:
        integer_str: String representation of integer part
        
    Returns:
        Formatted string with BDT-style commas
    """
    if len(integer_str) <= 3:
        return integer_str
    
    # Reverse the string for easier processing
    reversed_digits = integer_str[::-1]
    formatted_parts = []
    
    # First group: 3 digits (thousands)
    formatted_parts.append(reversed_digits[:3])
    remaining = reversed_digits[3:]
    
    # Subsequent groups: 2 digits each (lakhs, crores, etc.)
    while remaining:
        if len(remaining) >= 2:
            formatted_parts.append(remaining[:2])
            remaining = remaining[2:]
        else:
            formatted_parts.append(remaining)
            break
    
    # Join with commas and reverse back
    formatted_reversed = ','.join(formatted_parts)
    return formatted_reversed[::-1]

@register.filter
def bdt_currency(value):
    """
    Format numbers as BDT currency with Tk symbol
    
    Args:
        value: Number to format
        
    Returns:
        Formatted string with Tk symbol and BDT-style formatting
    """
    formatted_amount = bdt_format(value)
    return f'Tk {formatted_amount}'

@register.filter  
def bdt_with_decimals(value, decimal_places=2):
    """
    Format numbers in BDT style with specified decimal places
    
    Args:
        value: Number to format
        decimal_places: Number of decimal places to show (default: 2)
        
    Returns:
        Formatted string with specified decimal places
    """
    if value is None or value == '':
        return '0.' + '0' * decimal_places
    
    try:
        num = Decimal(str(value))
        # Round to specified decimal places
        rounded = round(num, decimal_places)
        
        # Format with BDT style
        formatted = bdt_format(rounded)
        
        # Ensure decimal places are shown
        if '.' not in formatted:
            formatted += '.' + '0' * decimal_places
        else:
            decimal_part = formatted.split('.')[1]
            if len(decimal_part) < decimal_places:
                formatted += '0' * (decimal_places - len(decimal_part))
        
        return formatted
        
    except (InvalidOperation, ValueError, TypeError):
        return str(value)

@register.filter
def inword(value):
    """
    Convert numbers to words (e.g., 1500 -> "One Thousand Five Hundred")
    
    Args:
        value: Number to convert to words
        
    Returns:
        String representation of the number in words
    """
    if value is None or value == '':
        return 'Zero'
    
    try:
        num = int(float(str(value)))
        return _number_to_words(num)
    except (ValueError, TypeError):
        return str(value)

def _number_to_words(num):
    """
    Convert integer to words using Indian numbering system
    """
    if num == 0:
        return 'Zero'
    
    # Handle negative numbers
    if num < 0:
        return 'Minus ' + _number_to_words(-num)
    
    # Number word mappings
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
            'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
            'Seventeen', 'Eighteen', 'Nineteen']
    
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    
    def convert_hundreds(n):
        """Convert numbers less than 1000 to words"""
        result = ''
        
        if n >= 100:
            result += ones[n // 100] + ' Hundred'
            n %= 100
            if n > 0:
                result += ' '
        
        if n >= 20:
            result += tens[n // 10]
            n %= 10
            if n > 0:
                result += ' ' + ones[n]
        elif n > 0:
            result += ones[n]
        
        return result
    
    # Handle different scales (Indian numbering system)
    if num >= 10000000:  # Crore
        crores = num // 10000000
        result = convert_hundreds(crores) + ' Crore'
        num %= 10000000
        if num > 0:
            result += ' ' + _number_to_words(num)
        return result
    
    elif num >= 100000:  # Lakh
        lakhs = num // 100000
        result = convert_hundreds(lakhs) + ' Lakh'
        num %= 100000
        if num > 0:
            result += ' ' + _number_to_words(num)
        return result
    
    elif num >= 1000:  # Thousand
        thousands = num // 1000
        result = convert_hundreds(thousands) + ' Thousand'
        num %= 1000
        if num > 0:
            result += ' ' + _number_to_words(num)
        return result
    
    else:
        return convert_hundreds(num)

@register.filter
def inword_currency(value):
    """
    Convert numbers to words with currency suffix (e.g., 1500 -> "One Thousand Five Hundred Taka Only")
    
    Args:
        value: Number to convert to words with currency
        
    Returns:
        String representation with currency suffix
    """
    if value is None or value == '':
        return 'Zero Taka Only'
    
    try:
        num = float(str(value))
        integer_part = int(num)
        decimal_part = int(round((num - integer_part) * 100))
        
        result = _number_to_words(integer_part) + ' Taka'
        
        if decimal_part > 0:
            result += ' and ' + _number_to_words(decimal_part) + ' Paisa'
        
        result += ' Only'
        return result
        
    except (ValueError, TypeError):
        return str(value)
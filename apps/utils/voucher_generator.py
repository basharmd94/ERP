"""
Simple and Flexible Voucher Number Generation System
"""

import re
from django.db import transaction, connection
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


def generate_voucher_number(zid: int, prefix: str, table: str, column: str, length: int = 6, xaction: str = None) -> str:
    """
    Generate next voucher number for any table and column combination

    Args:
        zid: Zone/Company ID for filtering
        prefix: Transaction prefix (e.g., 'RE--', 'PO--', 'GRN-')
        table: Database table name (e.g., 'imtrn', 'poord', 'pogrn')
        column: Column name containing voucher numbers (e.g., 'ximtmptrn', 'xpornum')
        length: Number padding length (default: 6)
        xaction: Transaction type for additional filtering (default: None)

    Returns:
        Next voucher number (e.g., 'RE--001035')

    Example:
        voucher = generate_voucher_number(100001, 'RE--', 'imtrn', 'ximtmptrn')
        # Returns: 'RE--001035'

        voucher_with_action = generate_voucher_number(100001, 'RE--', 'imtrn', 'ximtmptrn', xaction='RETURN')
        # Returns: 'RE--001036' (filtered by xaction)
    """

    def extract_numeric_part(voucher_number: str, prefix: str) -> int:
        """Extract numeric part from voucher number"""
        if not voucher_number or not voucher_number.startswith(prefix):
            return 0

        # Remove prefix to get numeric part
        numeric_part = voucher_number[len(prefix):]

        # Extract only digits
        digits = re.findall(r'\d+', numeric_part)
        if digits:
            return int(digits[0])

        return 0

    def format_voucher_number(prefix: str, number: int, length: int) -> str:
        """Format voucher number with proper padding"""
        return f"{prefix}{number:0{length}d}"

    try:
        with transaction.atomic():
            # Use raw SQL with SELECT FOR UPDATE to prevent race conditions
            with connection.cursor() as cursor:
                # Build SQL query with optional xaction filtering
                if xaction is not None:
                    sql = f"""
                        SELECT {column}
                        FROM {table}
                        WHERE zid = %s AND {column} LIKE %s AND xaction = %s
                        ORDER BY {column} DESC
                        LIMIT 1
                        FOR UPDATE
                    """
                    params = [zid, f"%{prefix}%", xaction]
                else:
                    sql = f"""
                        SELECT {column}
                        FROM {table}
                        WHERE zid = %s AND {column} LIKE %s
                        ORDER BY {column} DESC
                        LIMIT 1
                        FOR UPDATE
                    """
                    params = [zid, f"%{prefix}%"]

                cursor.execute(sql, params)
                result = cursor.fetchone()

                if result and result[0]:
                    last_voucher = result[0]
                    last_number = extract_numeric_part(last_voucher, prefix)
                    next_number = last_number + 1
                else:
                    next_number = 1

                return format_voucher_number(prefix, next_number, length)

    except Exception as e:
        logger.error(f"Error generating voucher number for table {table}, column {column}, prefix {prefix}: {str(e)}")
        raise ValidationError(f"Failed to generate voucher number: {str(e)}")


# Usage Examples:
"""
# Main function - use this for any voucher generation
voucher = generate_voucher_number(100001, 'RE--', 'imtrn', 'ximtmptrn')
# Returns: 'RE--001035'

# Different table and prefix
po_number = generate_voucher_number(100001, 'PO--', 'poord', 'xpornum')
# Returns: 'PO--000123'

# Custom prefix for any table
custom_voucher = generate_voucher_number(100001, 'CUSTOM-', 'mytable', 'mycolumn')
# Returns: 'CUSTOM-000001'
"""

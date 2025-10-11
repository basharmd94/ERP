"""
Average Price Calculation Utility for Inventory Management
"""

from django.db import connection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_average_price(zid: int, xitem: str, current_date: str = None) -> float:
    """
    Calculate average price for an item based on historical transactions
    
    Args:
        zid: Zone/Company ID
        xitem: Item code
        current_date: Date for calculation (defaults to current date)
        
    Returns:
        Average price as float
        
    Example:
        avg_price = get_average_price(100001, '02-007')
        # Returns: 150.75
    """
    
    if current_date is None:
        current_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT CASE 
                         WHEN SUM(xqty * xsign) > 0 THEN SUM(xval * xsign) / SUM(xqty * xsign) 
                         ELSE 0 
                       END AS average 
                FROM imtrn 
                WHERE zid = %s 
                  AND xitem = %s 
                  AND xdate <= %s
            """
            
            cursor.execute(sql, [zid, xitem, current_date])
            result = cursor.fetchone()
            
            if result and result[0] is not None:
                average_price = float(result[0])
                logger.info(f"Average price for item {xitem}: {average_price}")
                return average_price
            else:
                logger.warning(f"No average price found for item {xitem}, returning 0")
                return 0.0
                
    except Exception as e:
        logger.error(f"Error calculating average price for item {xitem}: {str(e)}")
        return 0.0


def get_average_prices_bulk(zid: int, items: list, current_date: str = None) -> dict:
    """
    Calculate average prices for multiple items in bulk
    
    Args:
        zid: Zone/Company ID
        items: List of item codes
        current_date: Date for calculation (defaults to current date)
        
    Returns:
        Dictionary with item codes as keys and average prices as values
        
    Example:
        prices = get_average_prices_bulk(100001, ['02-007', '03-002'])
        # Returns: {'02-007': 150.75, '03-002': 324.0}
    """
    
    if current_date is None:
        current_date = datetime.now().strftime('%Y-%m-%d')
    
    result_dict = {}
    
    try:
        with connection.cursor() as cursor:
            # Create placeholders for IN clause
            placeholders = ','.join(['%s'] * len(items))
            
            sql = f"""
                SELECT xitem,
                       CASE 
                         WHEN SUM(xqty * xsign) > 0 THEN SUM(xval * xsign) / SUM(xqty * xsign) 
                         ELSE 0 
                       END AS average 
                FROM imtrn 
                WHERE zid = %s 
                  AND xitem IN ({placeholders})
                  AND xdate <= %s
                GROUP BY xitem
            """
            
            params = [zid] + items + [current_date]
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # Initialize all items with 0
            for item in items:
                result_dict[item] = 0.0
            
            # Update with actual values
            for row in results:
                xitem, average_price = row
                result_dict[xitem] = float(average_price) if average_price is not None else 0.0
            
            logger.info(f"Bulk average prices calculated for {len(items)} items")
            return result_dict
            
    except Exception as e:
        logger.error(f"Error calculating bulk average prices: {str(e)}")
        # Return dictionary with all items set to 0
        return {item: 0.0 for item in items}
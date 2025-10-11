from django.db import connection
import logging

# Set up logging
logger = logging.getLogger(__name__)


def items_check_inventory(items, zid):
    """
    Validate item quantities against real-time inventory

    Args:
        items: List of items with xitem and quantity
        zid: Current business context ID

    Returns:
        dict: {'success': bool, 'message': str, 'errors': list}
    """
    try:
        # Extract item codes from the items list
        item_codes = [item['xitem'] for item in items]

        if not item_codes:
            return {
                'success': False,
                'message': 'No items to validate',
                'errors': []
            }

        # Build SQL query to get current inventory for all items
        placeholders = ','.join(['%s'] * len(item_codes))
        sql_query = f"""
        SELECT
            xitem,
            SUM(xqty * xsign) as current_stock
        FROM imtrn
        WHERE zid = %s AND xitem IN ({placeholders})
        GROUP BY xitem
        """

        # Prepare parameters: zid + item_codes
        params = [zid] + item_codes

        # Execute query
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            inventory_results = cursor.fetchall()

        # Convert results to dictionary for easy lookup
        inventory_dict = {row[0]: float(row[1]) for row in inventory_results}

        # Validate each item
        validation_errors = []

        for item in items:
            xitem = item['xitem']
            requested_qty = float(item['quantity'])
            current_stock = inventory_dict.get(xitem, 0.0)

            if requested_qty > current_stock:
                validation_errors.append({
                    'xitem': xitem,
                    'xdesc': item.get('xdesc', ''),
                    'requested_quantity': requested_qty,
                    'available_stock': current_stock,
                    'message': f'Insufficient stock for {xitem}. Requested: {requested_qty}, Available: {current_stock}'
                })

        if validation_errors:
            return {
                'success': False,
                'message': 'Inventory validation failed',
                'errors': validation_errors
            }

        return {
            'success': True,
            'message': 'Inventory validation successful',
            'errors': []
        }

    except Exception as e:
        logger.error(f"Inventory validation error: {str(e)}")
        return {
            'success': False,
            'message': f'Inventory validation error: {str(e)}',
            'errors': []
        }

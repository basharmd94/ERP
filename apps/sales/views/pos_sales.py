from django.http import JsonResponse
from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction, connection

import json
import logging

# Set up logging
logger = logging.getLogger(__name__)



class SalesView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'sales'
    template_name = 'pos_sales.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context



@login_required
def pos_products_api(request):
    """
    AJAX endpoint for POS product search with stock calculation
    Returns data in Select2 format for autocomplete
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    search_term = request.GET.get('search', '').strip()
    page = int(request.GET.get('page', 1))
    page_size = 20

    if not search_term:
        return JsonResponse({
            'results': [],
            'pagination': {'more': False}
        })

    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({'error': 'No business context found'}, status=400)

        # Require minimum 2 characters for search
        if len(search_term) < 2:
            return JsonResponse({
                'results': [],
                'pagination': {'more': False}
            })

        # Build SQL query to get items with stock calculation
        from django.db import connection

        sql_query = """
        SELECT
            c.xitem,
            c.xdesc,
            c.xstdprice,
            c.xbarcode,
            COALESCE(SUM(i.xqty * i.xsign), 0) AS stock
        FROM
            caitem c
        LEFT JOIN
            imtrn i ON c.xitem = i.xitem AND c.zid = i.zid
        WHERE
            c.zid = %s
            AND (
                LOWER(c.xitem) LIKE LOWER(%s)
                OR LOWER(c.xdesc) LIKE LOWER(%s)
                OR LOWER(c.xbarcode) LIKE LOWER(%s)
            )
        GROUP BY
            c.xitem, c.xdesc, c.xstdprice, c.xbarcode
        ORDER BY
            c.xitem
        LIMIT %s OFFSET %s
        """

        # Prepare search parameters
        search_param = f"%{search_term}%"
        offset = (page - 1) * page_size
        params = [current_zid, search_param, search_param, search_param, page_size, offset]

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            columns = [col[0] for col in cursor.description]
            results_data = cursor.fetchall()

            # Convert to list of dictionaries and format for Select2
            results = []
            for row in results_data:
                row_dict = dict(zip(columns, row))
                results.append({
                    'id': row_dict['xitem'],
                    'text': f"{row_dict['xitem']} - {row_dict['xdesc'] or 'No Description'}",
                    'xitem': row_dict['xitem'],
                    'xdesc': row_dict['xdesc'],
                    'xstdprice': float(row_dict['xstdprice'] or 0),
                    'xbarcode': row_dict['xbarcode'],
                    'stock': float(row_dict['stock'] or 0)
                })

        return JsonResponse({
            'results': results,
            'pagination': {
                'more': len(results) == page_size
            }
        })

    except Exception as e:
        return JsonResponse({
            'error': f'Search failed: {str(e)}'
        }, status=500)


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


@csrf_exempt
@transaction.atomic
def pos_complete_sale(request):
    """
    AJAX endpoint to complete a POS sale with inventory validation
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        logger.info(f"Received sale data: {data}")
        
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({
                'success': False,
                'error': 'No business context found'
            }, status=400)
        
        # Extract items from the request data
        items = data.get('items', [])
        if not items:
            return JsonResponse({
                'success': False,
                'error': 'No items found in the order'
            }, status=400)
        
        # Validate inventory for all items
        inventory_validation = items_check_inventory(items, current_zid)
        
        if not inventory_validation['success']:
            # Return validation errors with detailed information
            return JsonResponse({
                'success': False,
                'message': inventory_validation['message'],
                'errors': inventory_validation['errors'],
                'validation_failed': True
            }, status=400)
        
        # If validation passes, log success and return success response
        logger.info(f"Inventory validation successful for order with {len(items)} items")
        
        # TODO: Implement actual sale processing (opord, opodt, imtrn table insertions)
        # This will be implemented in the next step
        
        return JsonResponse({
            'success': True,
            'order_number': 'ORD-2024-001',
            'message': 'Inventory validation successful. Sale ready to process.',
            'validation_passed': True
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Sale processing error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

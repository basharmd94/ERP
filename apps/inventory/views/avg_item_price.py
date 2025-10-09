from django.http import JsonResponse
from django.db import connection
import logging

logger = logging.getLogger(__name__)

"""
Average Item Price API Module
This module contains the API endpoint for fetching items with calculated average rates.
Used by Smart Item Selector for search functionality across multiple modules.
"""


def get_avg_item_price(request):
    """
    API endpoint to fetch items with calculated average rates
    Used by Smart Item Selector for search functionality
    
    Args:
        request: HTTP request object containing search query parameter 'q'
        
    Returns:
        JsonResponse: JSON response containing item data with average rates
        
    Query Parameters:
        q (str): Search query for item code or description (minimum 2 characters)
        
    Response Format:
        {
            "success": bool,
            "data": [
                {
                    "xitem": str,      # Item code
                    "xdesc": str,      # Item description
                    "avg_rate": float, # Calculated average rate
                    "qty": float       # Available quantity
                }
            ],
            "count": int,
            "query": str
        }
    """
    try:
        # Get search query parameter
        query = request.GET.get('q', '').strip()
        
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            logger.warning(f"No business context found for user: {request.user.username}")
            return JsonResponse({'error': 'No business context found'}, status=400)

        # Require minimum 2 characters for search
        if len(query) < 2:
            return JsonResponse({
                'success': True,
                'data': [],
                'message': 'Please enter at least 2 characters to search'
            })

        # Build SQL query to get items with average rates
        sql_query = """
        SELECT 
            i.xitem, 
            c.xdesc, 
            SUM(i.xqty * i.xsign) AS qty, 
            CASE 
                WHEN SUM(i.xqty) > 0 THEN AVG(ABS(i.xval) / i.xqty)
                ELSE 0 
            END AS avg_rate
        FROM 
            imtrn i 
        JOIN 
            caitem c ON i.xitem = c.xitem AND i.zid = c.zid
        WHERE 
            i.zid = %s 
            AND c.zid = %s 
            AND i.xqty <> 0 
            AND (
                LOWER(i.xitem) LIKE LOWER(%s) 
                OR LOWER(c.xdesc) LIKE LOWER(%s)
            )
        GROUP BY 
            i.xitem, c.xdesc
        HAVING 
            SUM(i.xqty * i.xsign) > 0
        ORDER BY 
            i.xitem
        LIMIT 20
        """

        # Prepare search parameters
        search_param = f"%{query}%"
        params = [current_zid, current_zid, search_param, search_param]

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()

            # Convert to list of dictionaries
            data = []
            for row in results:
                row_dict = dict(zip(columns, row))
                # Format the data for frontend consumption
                data.append({
                    'xitem': row_dict['xitem'],
                    'xdesc': row_dict['xdesc'],
                    'avg_rate': round(float(row_dict['avg_rate']) if row_dict['avg_rate'] else 0, 2),
                    'qty': round(float(row_dict['qty']) if row_dict['qty'] else 0, 3)
                })

        logger.info(f"Item search executed - ZID: {current_zid}, Query: '{query}', Results: {len(data)}")

        return JsonResponse({
            'success': True,
            'data': data,
            'count': len(data),
            'query': query
        })

    except Exception as e:
        logger.error(f"Error fetching item data: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to fetch item data: {str(e)}'
        }, status=500)
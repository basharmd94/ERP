from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection
import logging

logger = logging.getLogger(__name__)


@login_required
def avg_item_price(request):
    """
    AJAX endpoint for average item price search with stock and value calculation
    Returns data in Select2 format for autocomplete

    Formulas:
    - Stock: sum(xqty * xsign)
    - Average Price: sum(xval * xsign) / sum(xqty * xsign) (handles divide by 0)
    """
    if request.method != 'GET':
        logger.error(f"Invalid method {request.method} for avg_item_price endpoint")
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
            logger.error("No business context found in session for avg_item_price endpoint")
            return JsonResponse({'error': 'No business context found'}, status=400)


        # Require minimum 2 characters for search
        if len(search_term) < 2:
            return JsonResponse({
                'results': [],
                'pagination': {'more': False}
            })

        # Build SQL query to get items with stock and average price calculation
        sql_query = """
        SELECT
            c.xitem,
            c.xdesc,
            c.xbarcode,
            c.xstdcost,
            c.xstdprice,
            c.xunitstk,
            COALESCE(SUM(i.xqty * i.xsign), 0) AS stock,
            COALESCE(SUM(i.xval * i.xsign), 0) AS total_value,
            CASE
                WHEN COALESCE(SUM(i.xqty * i.xsign), 0) = 0 THEN 0
                ELSE COALESCE(SUM(i.xval * i.xsign), 0) / COALESCE(SUM(i.xqty * i.xsign), 1)
            END AS avg_price
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
            c.xitem, c.xdesc, c.xbarcode, c.xstdcost, c.xstdprice, c.xunitstk
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
                    'xbarcode': row_dict['xbarcode'],
                    'xstdcost': float(row_dict['xstdcost'] or 0),
                    'xstdprice': float(row_dict['xstdprice'] or 0),
                    'xunitstk': row_dict['xunitstk'],
                    'stock': float(row_dict['stock'] or 0),
                    'total_value': float(row_dict['total_value'] or 0),
                    'avg_price': float(row_dict['avg_price'] or 0)
                })

        return JsonResponse({
            'results': results,
            'pagination': {
                'more': len(results) == page_size
            }
        })
        logger.info(f"Successfully processed avg_item_price search for term '{search_term}' with page {page}")

    except Exception as e:
        logger.error(f"Error in avg_item_price endpoint: {str(e)}")
        return JsonResponse({
            'error': f'Search failed: {str(e)}'
        }, status=500)

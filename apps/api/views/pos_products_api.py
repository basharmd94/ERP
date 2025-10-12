from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection


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
        sql_query = """
        SELECT
            c.xitem,
            c.xdesc,
            c.xstdprice,
            c.xbarcode,
            c.xstdcost,
            c.xunitstk,
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
            c.xitem, c.xdesc, c.xstdprice, c.xbarcode, c.xstdcost, c.xunitstk
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
                    'item_cost': float(row_dict['xstdcost'] or 0),
                    'xunitstk': row_dict['xunitstk'],
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
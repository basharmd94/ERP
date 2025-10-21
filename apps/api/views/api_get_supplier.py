from django.http import JsonResponse
from django.db import connection
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
def api_get_supplier(request):

    logger = logging.getLogger(__name__)

    try:
        search_term = request.GET.get('q', '').strip()
        try:
            page = int(request.GET.get('page', 1))
        except (ValueError, TypeError):
            page = 1

        page_size = 20

        with connection.cursor() as cursor:
            sql = """
                SELECT xsup, xshort
                FROM casup
                WHERE zid = %s
            """
            params = [request.session.get('current_zid', 100002)]

            if search_term:
                sql += " AND (LOWER(xsup) LIKE LOWER(%s) OR LOWER(xshort) LIKE LOWER(%s))"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern])

            sql += " ORDER BY xsup LIMIT %s OFFSET %s"
            offset = (page - 1) * page_size
            params.extend([page_size, offset])

            cursor.execute(sql, params)
            suppliers = cursor.fetchall()

        results = [
            {'id': xsup, 'text': xsup, 'xshort': xshort}
            for xsup, xshort in suppliers
        ]

        has_more = len(results) == page_size

        return JsonResponse({'results': results, 'pagination': {'more': has_more}})

    except Exception as e:
        logger.error(f'Error in api_get_supplier: {e}')
        return JsonResponse({
            'results': [],
            'pagination': {'more': False},
            'error': 'Failed to fetch suppliers'
        }, status=500)

from django.http import JsonResponse
from django.db import connection
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
def api_get_customer(request):

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
                SELECT xcus, xshort
                FROM cacus
                WHERE zid = %s
            """
            params = [request.session.get('current_zid')]

            if search_term:
                sql += " AND (LOWER(xcus) LIKE LOWER(%s) OR LOWER(xshort) LIKE LOWER(%s))"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern])

            sql += " ORDER BY xcus LIMIT %s OFFSET %s"
            offset = (page - 1) * page_size
            params.extend([page_size, offset])

            cursor.execute(sql, params)
            customers = cursor.fetchall()

        results = [
            {'id': xcus, 'text': xcus, 'xshort': xshort}
            for xcus, xshort in customers
        ]

        has_more = len(results) == page_size

        return JsonResponse({'results': results, 'pagination': {'more': has_more}})

    except Exception as e:
        logger.error(f'Error in api_get_customer: {e}')
        return JsonResponse({
            'results': [],
            'pagination': {'more': False},
            'error': 'Failed to fetch customers'
        }, status=500)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection
import logging

# Set up logging
logger = logging.getLogger(__name__)



@login_required
def api_get_project(request):
    """
    AJAX endpoint for project list
    Returns data in Select2 format
    """
    try:
        search_term = request.GET.get('q', '').strip()

        with connection.cursor() as cursor:
            # Base query to get project codes
            sql = """
                SELECT xcode
                FROM xcodes
                WHERE zid = %s AND xtype = 'Project'
            """
            params = [request.session.get('current_zid')]
            logger.info(f'Querying projects for ZID: {params[0]}')

            # Add search filter if search term provided
            if search_term:
                sql += " AND LOWER(xcode) LIKE LOWER(%s)"
                params.append(f'%{search_term}%')

            sql += " ORDER BY xcode"

            cursor.execute(sql, params)
            projects = cursor.fetchall()

        # Format data for Select2
        results = []
        for project in projects:
            results.append({
                'id': project[0],
                'text': project[0]
            })

        return JsonResponse({
            'results': results,
            'pagination': {'more': False}
        })

    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching project data: {str(e)}',
            'results': [],
            'pagination': {'more': False}
        }, status=500)

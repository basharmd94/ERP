from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection
import logging

# Import xcode types configuration
from .xcode_types import VALID_XTYPES, get_db_xtype, is_valid_xtype, get_valid_xtypes

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def api_get_xcodes(request, xtype):
    """
    Generic AJAX endpoint for xcode list based on xtype
    Returns data in Select2 format
    
    Args:
        xtype: The type of xcode to fetch (brands, units, item-group, etc.)
    """
    try:
        # Validate xtype parameter
        if not is_valid_xtype(xtype):
            return JsonResponse({
                'error': f'Invalid xtype: {xtype}. Valid types: {", ".join(get_valid_xtypes())}',
                'results': [],
                'pagination': {'more': False}
            }, status=400)
        
        # Get the actual xtype value for database query
        db_xtype = get_db_xtype(xtype)
        search_term = request.GET.get('q', '').strip()

        with connection.cursor() as cursor:
            # Base query to get xcodes
            sql = """
                SELECT xcode
                FROM xcodes
                WHERE zid = %s AND xtype = %s
            """
            params = [request.session.get('current_zid'), db_xtype]
            logger.info(f'Querying {xtype} for ZID: {params[0]}')

            # Add search filter if search term provided
            if search_term:
                sql += " AND LOWER(xcode) LIKE LOWER(%s)"
                params.append(f'%{search_term}%')

            sql += " ORDER BY xcode"

            cursor.execute(sql, params)
            xcodes = cursor.fetchall()

        # Format data for Select2
        results = []
        for xcode in xcodes:
            results.append({
                'id': xcode[0],
                'text': xcode[0]
            })

        return JsonResponse({
            'results': results,
            'pagination': {'more': False}
        })

    except Exception as e:
        logger.error(f'Error fetching {xtype} data: {str(e)}')
        return JsonResponse({
            'error': f'Error fetching {xtype} data: {str(e)}',
            'results': [],
            'pagination': {'more': False}
        }, status=500)
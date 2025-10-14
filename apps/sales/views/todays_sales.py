from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.db import connection
from datetime import date
import logging

logger = logging.getLogger(__name__)

@login_required
@csrf_protect
@require_http_methods(["GET"])
def todays_sales_ajax(request):
    """
    AJAX endpoint to fetch today's confirmed sales data
    Returns: xcus, xordernum, xtotamt, xsltype, xdtcomm from opord table
    """
    try:
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({'error': 'No business context found'}, status=400)

        # Get today's date
        today = date.today()

        with connection.cursor() as cursor:
            # Simple query to get today's confirmed sales
            query = """
                SELECT xcus, xordernum, xtotamt, xsltype, xdtcomm, xdate
                FROM opord
                WHERE zid = %s 
                AND DATE(xdate) = %s 
                AND xstatusord = 'Confirmed'
                ORDER BY xdate DESC
            """

            cursor.execute(query, [current_zid, today])
            rows = cursor.fetchall()

            # Format data for response
            data = []
            for row in rows:
                data.append([
                    row[5].strftime('%Y-%m-%d') if row[5] else '',  # xdate
                    row[1] or '',  # xordernum
                    row[0] or '',  # xcus
                    'Confirmed',   # status (always confirmed)
                    row[3] or '',  # xsltype (Cash/Card Sale)
                    '',            # warehouse (placeholder)
                    row[3] or '',  # payment type (xsltype)
                    float(row[4]) if row[4] else 0.00,  # xdtcomm (Card Amount)
                    float(row[2]) if row[2] else 0.00   # xtotamt (Total Amount)
                ])

            response = {
                'data': data,
                'recordsTotal': len(data),
                'recordsFiltered': len(data)
            }

            return JsonResponse(response)

    except Exception as e:
        logger.error(f"Error in todays_sales_ajax: {str(e)}")
        return JsonResponse({
            'error': 'Failed to fetch today\'s sales data',
            'details': str(e)
        }, status=500)


@login_required
@csrf_protect
@require_http_methods(["GET"])
def todays_sales_summary(request):
    """
    API endpoint to get summary statistics for today's confirmed sales
    """
    try:
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({'error': 'No business context found'}, status=400)

        # Get today's date
        today = date.today()

        with connection.cursor() as cursor:
            # Get summary statistics
            summary_query = """
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(xtotamt) as total_sales
                FROM opord
                WHERE zid = %s 
                AND DATE(xdate) = %s 
                AND xstatusord = 'Confirmed'
            """

            cursor.execute(summary_query, [current_zid, today])
            summary_row = cursor.fetchone()
            
            response_data = {
                'success': True,
                'total_orders': summary_row[0] or 0,
                'total_sales': float(summary_row[1]) if summary_row[1] else 0.00,
                'date': today.strftime('%Y-%m-%d')
            }

            return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Error in todays_sales_summary: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to fetch today\'s sales summary',
            'details': str(e)
        }, status=500)
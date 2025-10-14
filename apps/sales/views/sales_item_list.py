from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.db import connection
import logging

logger = logging.getLogger(__name__)

@login_required
@csrf_protect
@require_http_methods(["GET"])
def sales_item_list_ajax(request):
    """
    AJAX endpoint for DataTable to fetch sales item list data
    """
    try:
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({'error': 'No business context found'}, status=400)

        # DataTable parameters
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')

        # Order parameters
        order_column_index = int(request.GET.get('order[0][column]', 0))
        order_direction = request.GET.get('order[0][dir]', 'desc')

        # Column mapping for ordering
        columns = ['xdate', 'xordernum', 'xstatusord', 'xwh', 'xsltype', 'xsalescat', 'xdtcomm', 'xtotamt']
        order_column = columns[order_column_index] if order_column_index < len(columns) else 'xdate'

        # Base query
        base_query = """
            SELECT xdate, xordernum, xstatusord, xwh, xsltype, xsalescat, xdtcomm, xtotamt
            FROM opord
            WHERE zid = %s
        """

        # Search filter
        search_condition = ""
        params = [current_zid]

        if search_value:
            search_condition = """
                AND (
                    xordernum LIKE %s OR
                    xstatusord LIKE %s OR
                    xwh LIKE %s OR
                    xsltype LIKE %s OR
                    xsalescat LIKE %s OR
                    CAST(xdate AS CHAR) LIKE %s OR
                    CAST(xdtcomm AS CHAR) LIKE %s OR
                    CAST(xtotamt AS CHAR) LIKE %s
                )
            """
            search_params = [f'%{search_value}%'] * 8
            params.extend(search_params)

        # Count total records
        count_query = f"""
            SELECT COUNT(*) as total
            FROM opord
            WHERE zid = %s
            {search_condition}
        """

        with connection.cursor() as cursor:
            # Get total count
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()[0]

            # Get filtered data with pagination and ordering
            data_query = f"""
                {base_query}
                {search_condition}
                ORDER BY {order_column} {order_direction}
                LIMIT %s OFFSET %s
            """

            cursor.execute(data_query, params + [length, start])
            rows = cursor.fetchall()

            # Format data for DataTable
            data = []
            for row in rows:
                # Format date
                formatted_date = row[0].strftime('%Y-%m-%d') if row[0] else ''

                # Format payment type (Cash/Card)
                payment_type = row[4] or ''  # xsltype

                # Format bank name
                bank_name = row[5] or ''  # xsalescat

                # Format card amount
                card_amount = float(row[6]) if row[6] else 0.00  # xdtcomm

                # Format total amount - send as number for frontend formatting
                formatted_amount = float(row[7]) if row[7] else 0.00  # xtotamt

                # Create action buttons
                actions = f"""
                    <div class="dropdown">
                        <button type="button" class="btn btn-sm btn-outline-secondary dropdown-toggle"
                                data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="tf-icons ti ti-dots-vertical"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#" onclick="viewSalesOrder('{row[1]}')">
                                <i class="tf-icons ti ti-eye me-1"></i>View</a></li>
                            <li><a class="dropdown-item" href="#" onclick="editSalesOrder('{row[1]}')">
                                <i class="tf-icons ti ti-edit me-1"></i>Edit</a></li>
                            <li><a class="dropdown-item" href="#" onclick="printSalesOrder('{row[1]}')">
                                <i class="tf-icons ti ti-printer me-1"></i>Print</a></li>
                            <li><a class="dropdown-item" href="#" onclick="printPosInvoice('{row[1]}')">
                                <i class="tf-icons ti ti-receipt me-1"></i>Print POS Invoice</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item text-danger" href="#" onclick="deleteSalesOrder('{row[1]}')">
                                <i class="tf-icons ti ti-trash me-1"></i>Delete</a></li>
                        </ul>
                    </div>
                """

                data.append([
                    formatted_date,
                    row[1] or '',  # xordernum
                    row[2] or '',  # xstatusord
                    row[3] or '',  # xwh
                    payment_type,  # xsltype
                    bank_name,     # xsalescat
                    card_amount,   # xdtcomm
                    formatted_amount,  # xtotamt
                    actions
                ])

            response = {
                'draw': draw,
                'recordsTotal': total_records,
                'recordsFiltered': total_records,
                'data': data
            }

            return JsonResponse(response)

    except Exception as e:
        logger.error(f"Error in sales_item_list_ajax: {str(e)}")
        return JsonResponse({
            'error': 'Failed to fetch data',
            'details': str(e)
        }, status=500)

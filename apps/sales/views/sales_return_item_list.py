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
def sales_return_item_list(request):
    """
    AJAX endpoint for DataTable to fetch sales return item list data
    """
    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        logger.info(f"Sales return item list - current_zid from session: {current_zid}")

        if not current_zid:
            return JsonResponse({'error': 'No business context found'}, status=400)

        # DataTable parameters
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '').strip()

        # Order parameters
        order_column_index = int(request.GET.get('order[0][column]', 0))
        order_direction = request.GET.get('order[0][dir]', 'desc')

        # Column mapping for ordering (excluding action column)
        columns = ['xdate', 'ximtmptrn', 'xwh', 'xglref', 'xstatustrn']
        order_column = columns[order_column_index] if 0 <= order_column_index < len(columns) else 'xdate'

        # Validate order direction
        if order_direction not in ['asc', 'desc']:
            order_direction = 'desc'

        # Build base query
        base_query = """
            SELECT xdate, ximtmptrn, xwh, xglref, xstatustrn
            FROM imtemptrn
            WHERE zid = %s AND ximtmptrn LIKE %s
        """

        # Base parameters
        base_params = [current_zid, '%SRE-%']

        # Add search conditions if search value provided
        search_conditions = []
        search_params = []

        if search_value:
            search_conditions = [
                "ximtmptrn LIKE %s",
                "xwh LIKE %s",
                "xglref LIKE %s",
                "xstatustrn LIKE %s",
                "CAST(xdate AS CHAR) LIKE %s"
            ]
            search_params = [f'%{search_value}%'] * 5

        # Build complete WHERE clause
        where_clause = "WHERE zid = %s AND ximtmptrn LIKE %s"
        query_params = base_params.copy()

        if search_conditions:
            where_clause += " AND (" + " OR ".join(search_conditions) + ")"
            query_params.extend(search_params)

        with connection.cursor() as cursor:
            # Get total count (without search filter)
            count_query = "SELECT COUNT(*) FROM imtemptrn WHERE zid = %s AND ximtmptrn LIKE %s"
            logger.info(f"Executing count query: {count_query} with params: {base_params}")

            cursor.execute(count_query, base_params)
            count_result = cursor.fetchone()
            total_records = count_result[0] if count_result else 0
            logger.info(f"Total records found: {total_records}")

            # Get filtered count (with search filter if applied)
            if search_value:
                filtered_count_query = f"SELECT COUNT(*) FROM imtemptrn {where_clause}"
                logger.info(f"Executing filtered count query: {filtered_count_query} with params: {query_params}")
                cursor.execute(filtered_count_query, query_params)
                filtered_result = cursor.fetchone()
                filtered_records = filtered_result[0] if filtered_result else 0
            else:
                filtered_records = total_records

            logger.info(f"Filtered records found: {filtered_records}")

            # Get data with pagination and ordering
            data_query = f"""
                SELECT xdate, ximtmptrn, xwh, xglref, xstatustrn
                FROM imtemptrn
                {where_clause}
                ORDER BY {order_column} {order_direction}
                LIMIT %s OFFSET %s
            """

            final_params = query_params + [length, start]
            logger.info(f"Executing data query: {data_query}")
            logger.info(f"Data query params: {final_params}")

            cursor.execute(data_query, final_params)
            rows = cursor.fetchall()
            logger.info(f"Data query returned {len(rows)} rows")

            # Format data for DataTable
            data = []
            for i, row in enumerate(rows):
                try:
                    # Safely access row data with bounds checking
                    if len(row) < 5:
                        logger.warning(f"Row {i} has insufficient columns: {len(row)} columns, expected 5")
                        continue

                    # Format date safely
                    formatted_date = ''
                    if row[0]:
                        try:
                            formatted_date = row[0].strftime('%Y-%m-%d')
                        except (AttributeError, ValueError) as e:
                            logger.warning(f"Date formatting error for row {i}: {e}")
                            formatted_date = str(row[0]) if row[0] else ''

                    # Get SRE number safely
                    sre_number = str(row[1]) if row[1] else ''
                    warehouse = str(row[2]) if row[2] else ''
                    gl_ref = str(row[3]) if row[3] else ''
                    status = str(row[4]) if row[4] else ''

                    # Create Quick Act buttons with delete button
                    quick_actions = f"""
                        <div class="btn-group" role="group" aria-label="Quick Actions">
                            <a href="/sales/sales-return-detail/{sre_number}/"
                               target="_blank"
                               class="btn btn-sm btn-outline-primary"
                               title="View Details">
                                <i class="tf-icons ti ti-eye"></i>
                            </a>
                            <a href="/sales/sales-return-print/{sre_number}/"
                               target="_blank"
                               class="btn btn-sm btn-outline-info"
                               title="Print">
                                <i class="tf-icons ti ti-printer"></i>
                            </a>
                            <a href="/sales/sales-return-export-excel/{sre_number}/"
                               class="btn btn-sm btn-outline-success"
                               title="Export Excel">
                                <i class="tf-icons ti ti-file-spreadsheet"></i>
                            </a>
                            <button type="button"
                                    class="btn btn-sm btn-outline-danger"
                                    onclick="deleteSalesReturn('{sre_number}')"
                                    title="Delete">
                                <i class="tf-icons ti ti-trash"></i>
                            </button>
                        </div>
                    """

                    data.append([
                        formatted_date,
                        sre_number,
                        warehouse,
                        gl_ref,
                        status,
                        quick_actions
                    ])

                except Exception as row_error:
                    logger.error(f"Error processing row {i}: {row_error}, row data: {row}")
                    continue

            # Prepare response
            response = {
                'draw': draw,
                'recordsTotal': total_records,
                'recordsFiltered': filtered_records,
                'data': data
            }

            logger.info(f"Returning response with {len(data)} data rows")
            return JsonResponse(response)

    except Exception as e:
        logger.error(f"Error in sales_return_item_list: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to fetch sales return data',
            'details': str(e)
        }, status=500)

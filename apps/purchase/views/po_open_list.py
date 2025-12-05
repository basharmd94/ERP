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
def po_open_list(request):
    try:
        zid = request.session.get('current_zid') or 100001
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '').strip()

        order_column_index = int(request.GET.get('order[0][column]', 0))
        order_direction = request.GET.get('order[0][dir]', 'desc')
        if order_direction not in ['asc', 'desc']:
            order_direction = 'desc'

        columns = ['po.xdate', 'po.xpornum', 'grn.xgrnnum', 'po.xsup', 's.xshort', 'po.xstatuspor']
        order_column = columns[order_column_index] if 0 <= order_column_index < len(columns) else 'po.xdate'

        base_where = "po.zid = %s AND s.zid = %s AND po.xstatuspor = '1-Open'"
        base_params = [zid, zid]

        search_conditions = []
        search_params = []
        if search_value:
            search_conditions = [
                "po.xpornum LIKE %s",
                "grn.xgrnnum LIKE %s",
                "po.xsup LIKE %s",
                "s.xshort LIKE %s",
                "po.xstatuspor LIKE %s",
                "CAST(po.xdate AS CHAR) LIKE %s",
            ]
            like = f"%{search_value}%"
            search_params = [like, like, like, like, like, like]

        with connection.cursor() as cursor:
            count_query = (
                f"SELECT COUNT(*) FROM poord po "
                f"JOIN casup s ON po.xsup = s.xsup AND po.zid = s.zid "
                f"LEFT JOIN pogrn grn ON grn.xpornum = po.xpornum AND grn.zid = po.zid AND grn.xstatusgrn = '1-Open' "
                f"WHERE {base_where}"
            )
            cursor.execute(count_query, base_params)
            total_records = cursor.fetchone()[0]

            if search_conditions:
                where_clause = base_where + " AND (" + " OR ".join(search_conditions) + ")"
                filtered_count_query = (
                    f"SELECT COUNT(*) FROM poord po "
                    f"JOIN casup s ON po.xsup = s.xsup AND po.zid = s.zid "
                    f"LEFT JOIN pogrn grn ON grn.xpornum = po.xpornum AND grn.zid = po.zid AND grn.xstatusgrn = '1-Open' "
                    f"WHERE {where_clause}"
                )
                cursor.execute(filtered_count_query, base_params + search_params)
                filtered_records = cursor.fetchone()[0]
            else:
                filtered_records = total_records

            data_query = f"""
                SELECT po.xdate, po.xpornum, grn.xgrnnum AS xgrnnum, po.xsup, s.xshort AS supplier_name, po.xstatuspor
                FROM poord po
                JOIN casup s ON po.xsup = s.xsup AND po.zid = s.zid
                LEFT JOIN pogrn grn ON grn.xpornum = po.xpornum AND grn.zid = po.zid AND grn.xstatusgrn = '1-Open'
                WHERE {base_where}
            """
            params = base_params
            if search_conditions:
                data_query += " AND (" + " OR ".join(search_conditions) + ")"
                params = base_params + search_params
            data_query += f" ORDER BY {order_column} {order_direction} LIMIT %s OFFSET %s"
            params += [length, start]

            cursor.execute(data_query, params)
            rows = cursor.fetchall()

        data = []
        for row in rows:
            date_val = ''
            if row[0]:
                try:
                    date_val = row[0].strftime('%Y-%m-%d')
                except Exception:
                    date_val = str(row[0])
            xpornum = str(row[1]) if row[1] else ''
            xgrnnum = str(row[2]) if row[2] else ''
            xsup = str(row[3]) if row[3] else ''
            supplier_name = str(row[4]) if row[4] else ''
            status = str(row[5]) if row[5] else ''
            data.append([
                date_val,
                xpornum,
                xgrnnum,
                xsup,
                supplier_name,
                status,
                xpornum,  # Confirm column data (PO Number)
                xpornum,  # Quick Act column data (PO Number)
                xpornum   # Actions column data (PO Number)
            ])

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data
        })
    except Exception as e:
        return JsonResponse({'error': 'Failed to fetch purchase orders', 'details': str(e)}, status=500)

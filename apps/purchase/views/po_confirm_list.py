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
def po_confirm_list(request):
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

        columns = ['grn.xdate', 'po.xpornum', 'grn.xgrnnum', 'po.xsup', 's.xshort', 'grn.xstatusgrn', 'grn.xref']
        order_column = columns[order_column_index] if 0 <= order_column_index < len(columns) else 'grn.xdate'

        base_where = "grn.zid = %s AND po.zid = %s AND s.zid = %s AND grn.xstatusgrn = '5-Confirmed'"
        base_params = [zid, zid, zid]

        search_conditions = []
        search_params = []
        if search_value:
            search_conditions = [
                "po.xpornum LIKE %s",
                "grn.xgrnnum LIKE %s",
                "po.xsup LIKE %s",
                "s.xshort LIKE %s",
                "grn.xstatusgrn LIKE %s",
                "grn.xref LIKE %s",
                "CAST(grn.xdate AS CHAR) LIKE %s",
            ]
            like = f"%{search_value}%"
            search_params = [like, like, like, like, like, like, like]

        with connection.cursor() as cursor:
            count_query = (
                f"SELECT COUNT(*) FROM pogrn grn "
                f"JOIN poord po ON grn.xpornum = po.xpornum AND grn.zid = po.zid "
                f"JOIN casup s ON po.xsup = s.xsup AND po.zid = s.zid "
                f"WHERE {base_where}"
            )
            cursor.execute(count_query, base_params)
            total_records = cursor.fetchone()[0]

            if search_conditions:
                where_clause = base_where + " AND (" + " OR ".join(search_conditions) + ")"
                filtered_count_query = (
                    f"SELECT COUNT(*) FROM pogrn grn "
                    f"JOIN poord po ON grn.xpornum = po.xpornum AND grn.zid = po.zid "
                    f"JOIN casup s ON po.xsup = s.xsup AND po.zid = s.zid "
                    f"WHERE {where_clause}"
                )
                cursor.execute(filtered_count_query, base_params + search_params)
                filtered_records = cursor.fetchone()[0]
            else:
                filtered_records = total_records

            data_query = f"""
                SELECT grn.xdate, po.xpornum, grn.xgrnnum, po.xsup, s.xshort AS supplier_name, grn.xstatusgrn, grn.xref
                FROM pogrn grn
                JOIN poord po ON grn.xpornum = po.xpornum AND grn.zid = po.zid
                JOIN casup s ON po.xsup = s.xsup AND po.zid = s.zid
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
            invoice = str(row[6]) if row[6] else ''
            data.append([
                date_val,
                xpornum,
                xgrnnum,
                xsup,
                supplier_name,
                status,
                invoice,
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
        return JsonResponse({'error': 'Failed to fetch confirmed GRNs', 'details': str(e)}, status=500)


from django.http import HttpResponse
from django.db import connection
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime


@login_required
def sales_return_print(request, transaction_id):
    # Get current ZID from session
    session_zid = request.session.get('current_zid')

    # SQL query to get sales return data with business information and item descriptions
    sales_return_sql = """
        SELECT
            t.ximtmptrn,
            t.xdate,
            t.xrem,
            t.xproj,
            t.xwh,
            t.zemail,
            t.xglref,
            t.xstatustrn,
            d.xtorlno,
            d.xitem,
            d.xqtyord,
            d.xunit,
            d.ximtrnnum,
            d.xrate,
            d.xval,
            d.xlineamt,
            b.zid as business_id,
            b.name as business_name,
            b.address as business_address,
            b.mobile as business_mobile,
            b.website as business_website,
            c.xdesc as xitemdesc
        FROM imtemptrn t
        INNER JOIN imtemptdt d
            ON t.ximtmptrn = d.ximtmptrn
            AND t.zid = d.zid
        INNER JOIN authentication_business b
            ON t.zid = b.zid
        LEFT JOIN caitem c
            ON d.xitem = c.xitem
            AND d.zid = c.zid
        WHERE t.zid = %s
          AND t.ximtmptrn = %s
        ORDER BY d.xtorlno
    """

    with connection.cursor() as cursor:
        # Get sales return data
        cursor.execute(sales_return_sql, [session_zid, transaction_id])
        rows = cursor.fetchall()

        if not rows:
            # Debug information
            debug_sql = "SELECT zid, ximtmptrn FROM imtemptrn WHERE ximtmptrn = %s"
            cursor.execute(debug_sql, [transaction_id])
            debug_results = cursor.fetchall()

            debug_info = f"Sales return not found. Transaction ID: {transaction_id}, Session ZID: {session_zid}. "
            if debug_results:
                debug_info += f"Found transaction with different ZIDs: {debug_results}"
            else:
                debug_info += "No sales return found with this transaction ID in any ZID."

            return HttpResponse(debug_info, status=404)

        # Process the data
        header_data = None
        business_data = None
        line_items = []

        for row in rows:
            # Header data (same for all rows)
            if header_data is None:
                header_data = {
                    'ximtmptrn': row[0],
                    'xdate': row[1].strftime('%Y-%m-%d') if row[1] else '',
                    'xrem': row[2] or '',
                    'xproj': row[3] or '',
                    'xwh': row[4] or '',
                    'zemail': row[5] or '',
                    'xglref': row[6] or '',
                    'xstatustrn': row[7] or ''
                }

            # Business data (same for all rows)
            if business_data is None:
                business_data = {
                    'business_id': row[16],
                    'business_name': row[17] or '',
                    'business_address': row[18] or '',
                    'business_mobile': row[19] or '',
                    'business_website': row[20] or ''
                }

            # Line item data
            line_item = {
                'xtorlno': row[8] or '',
                'xitem': row[9] or '',
                'xqtyord': float(row[10]) if row[10] else 0.0,
                'xunit': row[11] or '',
                'ximtrnnum': row[12] or '',
                'xrate': float(row[15]) if row[13] else 0.0,
                'xval': float(row[14]) if row[14] else 0.0,
                'xlineamt': float(row[15]) if row[15] else 0.0,
                'xitemdesc': row[21] or ''
            }
            line_items.append(line_item)

        # Calculate totals
        total_quantity = sum(item['xqtyord'] for item in line_items)
        total_value = sum(item['xval'] for item in line_items)
        total_line_amount = sum(item['xlineamt'] for item in line_items)

        totals = {
            'total_quantity': total_quantity,
            'total_value': total_value,
            'total_line_amount': total_line_amount,
            'item_count': len(line_items)
        }

    # Render HTML template
    html_string = render_to_string('sales_return_print.html', {
        'header': header_data,
        'business': business_data,
        'line_items': line_items,
        'totals': totals,
        'session_zid': session_zid,
        'transaction_id': transaction_id,
        'print_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    # Generate PDF using xhtml2pdf
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

    if not pdf.err:
        # Return PDF response
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="sales_return_{transaction_id}.pdf"'
        return response
    else:
        return HttpResponse('Error generating PDF', status=500)


from django.http import HttpResponse
from django.db import connection
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
import logging

logger = logging.getLogger(__name__)



@login_required
def po_req_print(request, transaction_id):
    # Get current ZID from session
    session_zid = request.session.get('current_zid')

    if not session_zid:
        return HttpResponse("Session ZID not found", status=400)

    # SQL query to get purchase order data including preparer email (zemail)
    po_sql = """
        SELECT
            po.xpornum,
            po.xdate,
            po.xsup,
            s.xorg AS supplier_name,
            po.xproj,
            po.xwh,

            dt.xitem,
            it.xdesc,
            it.xunitstk,
            dt.xqtyord,

            COALESCE(stk.prev_stock, 0) AS previous_stock,

            s.xadd1 AS supplier_address,
            po.xsupref AS supplier_ref,
            po.zemail AS zemail

        FROM poord po
        JOIN poodt dt
            ON po.xpornum = dt.xpornum
            AND po.zid = dt.zid

        JOIN casup s
            ON po.xsup = s.xsup
            AND po.zid = s.zid

        JOIN caitem it
            ON dt.xitem = it.xitem
            AND dt.zid = it.zid

        LEFT JOIN (
            SELECT
                xitem,
                SUM(xqty * xsign) AS prev_stock
            FROM imtrn
            WHERE zid = %s
            GROUP BY xitem
        ) AS stk
            ON dt.xitem = stk.xitem

        WHERE
            po.zid = %s
            AND po.xpornum = %s

        ORDER BY dt.xitem
    """

    # Get business information
    business_sql = """
        SELECT name, address, mobile, website
        FROM authentication_business
        WHERE zid = %s
    """

    with connection.cursor() as cursor:
        # Fetch Business Info
        cursor.execute(business_sql, [session_zid])
        business_row = cursor.fetchone()
        if business_row:
            business_data = {
                'business_name': business_row[0] or 'Unknown Business',
                'business_address': business_row[1] or '',
                'business_mobile': business_row[2] or '',
                'business_email': '',
                'business_website': business_row[3] or ''
            }
        else:
            business_data = {
                'business_name': 'Unknown Business',
                'business_address': '',
                'business_mobile': '',
                'business_email': '',
                'business_website': ''
            }

        # Fetch PO Data (single query with zemail)
        cursor.execute(po_sql, [session_zid, session_zid, transaction_id])
        rows = cursor.fetchall()
        logger.info(f"Fetched {len(rows)} rows for PO {transaction_id}")


        if not rows:
            logger.error(f"Purchase Order not found: {transaction_id}")
            return HttpResponse(f"Purchase Order not found: {transaction_id}", status=404)


        # Process data
        header_data = None
        line_items = []

        for row in rows:
            if header_data is None:
                header_data = {
                    'xpornum': row[0],
                    'xdate': row[1].strftime('%d/%m/%y') if row[1] else '',
                    'xsup': row[2],
                    'supplier_name': row[3],
                    'xproj': row[4] or '',
                    'xwh': row[5],
                    'supplier_address': row[11] or '',
                    'supplier_ref': row[12] or '',
                    'zemail': row[13]
                }

            line_items.append({
                'xitem': row[6],
                'xdesc': row[7],
                'xunitstk': row[8],
                'xqtyord': row[9],
                'previous_stock': row[10]
            })

    # Render HTML template
    html_string = render_to_string('reports/po_req_print.html', {
        'header': header_data,
        'business': business_data,
        'line_items': line_items,
        'print_date': datetime.now().strftime('%d/%m/%y'),
        'current_year': datetime.now().year
    })

    # Generate PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

    if not pdf.err:
        logger.info(f"PDF generated successfully for PO {transaction_id}")
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="PO_{transaction_id}.pdf"'
        return response
    else:
        logger.error(f"Error generating PDF for PO {transaction_id}: {pdf.err}")
        return HttpResponse('Error generating PDF', status=500)

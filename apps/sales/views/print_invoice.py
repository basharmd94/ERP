
from django.http import HttpResponse
from django.db import connection
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from io import BytesIO


@login_required
def print_invoice(request, transaction_id):
    # Get current ZID from session
    session_zid = request.session.get('current_zid') 

    # SQL query to get order header information from opord table
    header_sql = """
    SELECT ztime, zid, xordernum, xdate, xcus, xstatusord, xcur,
           xdisc, xdiscf, xwh, xemail, xdtwotax, xdtdisc, xdttax,
           xval, xdiscamt, xtotamt, xsp, xsltype, xsalescat, xtrnord,
           xdocnum, xdtcomm, xcounterno, xyear, xper, xemp, xmobile,
           xdatecon, xamtpaid, xamt
    FROM opord
    WHERE zid = %s AND xordernum = %s
    """

    # SQL query to get order details from opodt table
    details_sql = """
    SELECT ztime, zid, xordernum, xrow, xcode, xitem, xstype, xwh,
           xqtyreq, xqtyord, xunitsel, xcur, xrate, xlineamt, xdtwotax,
           xdttax, ximtrnnum, xcost, xsign, xdesc
    FROM opodt
    WHERE zid = %s AND xordernum = %s
    ORDER BY xrow
    """

    with connection.cursor() as cursor:
        # Get order header
        cursor.execute(header_sql, [session_zid, transaction_id])
        header_columns = [col[0] for col in cursor.description]
        header_result = cursor.fetchone()

        if not header_result:
            # Debug information
            debug_sql = "SELECT zid, xordernum FROM opord WHERE xordernum = %s"
            cursor.execute(debug_sql, [transaction_id])
            debug_results = cursor.fetchall()
            
            debug_info = f"Order not found. Transaction ID: {transaction_id}, Session ZID: {session_zid}. "
            if debug_results:
                debug_info += f"Found order with different ZIDs: {debug_results}"
            else:
                debug_info += "No order found with this transaction ID in any ZID."
            
            return HttpResponse(debug_info, status=404)

        order_header = dict(zip(header_columns, header_result))

        # Get order details
        cursor.execute(details_sql, [session_zid, transaction_id])
        detail_columns = [col[0] for col in cursor.description]
        order_details = [dict(zip(detail_columns, row)) for row in cursor.fetchall()]

    # Render HTML template
    html_string = render_to_string('print_invoice.html', {
        'order_header': order_header,
        'order_details': order_details,
        'session_zid': session_zid,
        'transaction_id': transaction_id
    })

    # Generate PDF using xhtml2pdf
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

    if not pdf.err:
        # Return PDF response
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="sales_invoice_{transaction_id}.pdf"'
        return response
    else:
        return HttpResponse('Error generating PDF', status=500)

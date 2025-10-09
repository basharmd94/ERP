
from django.http import HttpResponse
from django.db import connection
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO

def last_10_orders(request):
    # Get session zid (you may need to adjust this based on your session handling)
    session_zid = request.session.get('zid', '100001')  # Default to '001' if not in session

    # Direct SQL query as requested
    sql = """
    SELECT ztime, zid, xordernum, xrow, xitem, xdesc, xstype, xwh,
           xqtyord, xqtyreq, xunitsel, xcur, xrate, xdtwotax, xdttax, ximtrnnum
    FROM opodt
    WHERE zid = %s
    LIMIT 5
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, [session_zid])
        columns = [col[0] for col in cursor.description]
        orders = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Render HTML template
    html_string = render_to_string('last_10_order.html', {
        'orders': orders,
        'session_zid': session_zid
    })

    # Generate PDF using xhtml2pdf
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

    if not pdf.err:
        # Return PDF response
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="last_10_orders.pdf"'
        return response
    else:
        return HttpResponse('Error generating PDF', status=500)

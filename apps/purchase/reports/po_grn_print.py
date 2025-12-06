from django.http import HttpResponse
from django.db import connection
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
def _fmt_date(d):
    try:
        return d.strftime('%d-%b-%Y') if d else ''
    except Exception:
        return str(d) if d else ''

@login_required
def po_grn_print(request, transaction_id):
    zid = request.session.get('current_zid')
    if not zid:
        return HttpResponse("Session ZID not found", status=400)

    business_sql = """
        SELECT name, address, mobile, website
        FROM authentication_business
        WHERE zid = %s
    """

    header_sql = """
        SELECT
            grn.xgrnnum,
            grn.xdate,
            grn.xsup,
            s.xorg AS supplier_name,
            s.xadd1 AS supplier_address,
            grn.xproj,
            grn.xwh,
            grn.xrem,
            grn.xdtwotax,
            grn.xdiscamt,
            grn.xdttax,
            grn.xtotamt,
            grn.xpornum,
            po.xdate AS po_date,
            grn.xconfirmt,
            grn.zemail,
            grn.xstatusgrn,
            grn.xref
        FROM pogrn grn
        LEFT JOIN casup s ON s.zid = grn.zid AND s.xsup = grn.xsup
        LEFT JOIN poord po ON po.zid = grn.zid AND po.xpornum = grn.xpornum
        WHERE grn.zid = %s AND grn.xgrnnum = %s
        LIMIT 1
    """

    details_sql = """
        SELECT
            d.xrow,
            d.xitem,
            i.xdesc,
            i.xunitstk,
            d.xqty,
            d.xqtygrn,
            d.xrate,
            d.xlineamt
        FROM pogdt d
        LEFT JOIN caitem i ON i.zid = d.zid AND i.xitem = d.xitem
        WHERE d.zid = %s AND d.xgrnnum = %s
        ORDER BY d.xrow
    """

    with connection.cursor() as cursor:
        cursor.execute(business_sql, [zid])
        br = cursor.fetchone()
        business = {
            'business_name': (br[0] if br else '') or 'Unknown Business',
            'business_address': (br[1] if br else '') or '',
            'business_mobile': (br[2] if br else '') or '',
            'business_email': '',
            'business_website': (br[3] if br else '') or ''
        }

        cursor.execute(header_sql, [zid, transaction_id])
        hr = cursor.fetchone()
        if not hr:
            return HttpResponse(f"GRN not found: {transaction_id}", status=404)

        header = {
            'xgrnnum': hr[0] or '',
            'xdate': _fmt_date(hr[1]),
            'xsup': hr[2] or '',
            'supplier_name': hr[3] or '',
            'supplier_address': hr[4] or '',
            'xproj': hr[5] or '',
            'xwh': hr[6] or '',
            'xrem': hr[7] or '',
            'xdtwotax': float(hr[8]) if hr[8] is not None else 0.0,
            'xdiscamt': float(hr[9]) if hr[9] is not None else 0.0,
            'xdttax': float(hr[10]) if hr[10] is not None else 0.0,
            'xtotamt': float(hr[11]) if hr[11] is not None else 0.0,
            'xpornum': hr[12] or '',
            'po_date': _fmt_date(hr[13]) if hr[13] else '',
            'xconfirmt': _fmt_date(hr[14]) if hr[14] else '',
            'zemail': hr[15] or '',
            'xstatusgrn': hr[16] or '',
            'xref': hr[17] or ''
        }

        cursor.execute(details_sql, [zid, transaction_id])
        rows = cursor.fetchall()
        line_items = []
        for r in rows:
            line_items.append({
                'xrow': int(r[0]) if r[0] else 0,
                'xitem': r[1] or '',
                'xdesc': r[2] or (r[1] or ''),
                'xunitstk': r[3] or '',
                'qty_supplied': float(r[4]) if r[4] is not None else 0.0,
                'qty_received': float(r[5]) if r[5] is not None else 0.0,
                'xrate': float(r[6]) if r[6] is not None else 0.0,
                'xlineamt': float(r[7]) if r[7] is not None else 0.0
            })

        totals = {
            'subtotal': header['xdtwotax'],
            'discount': header['xdiscamt'],
            'tax': header['xdttax'],
            'grand_total': header['xtotamt']
        }

    html = render_to_string('reports/po_grn_print.html', {
        'header': header,
        'line_items': line_items,
        'totals': totals,
        'business': business,
        'print_date': datetime.now().strftime('%d-%b-%Y'),
        'current_year': datetime.now().year,
        'transaction_id': transaction_id
    })

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
    if pdf.err:
        return HttpResponse('Error generating PDF', status=500)
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="GRN_{transaction_id}.pdf"'
    return response

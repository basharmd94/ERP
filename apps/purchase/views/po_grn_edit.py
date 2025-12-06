import json
from decimal import Decimal
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import connection, transaction
from django.utils import timezone
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin, ModulePermissionMixin


class POGrnEditView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    template_name = 'purchase_edit.html'
    module_code = 'po_grn_edit'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        transaction_id = kwargs.get('transaction_id')
        if transaction_id:
            context['transaction_id'] = transaction_id
        return context


@login_required
@csrf_protect
@require_http_methods(["GET"])
def po_grn_get(request, transaction_id: str):
    zid = request.session.get('current_zid')
    if not zid:
        return JsonResponse({'success': False, 'message': 'Session ZID not found'}, status=401)

    header_sql = """
        SELECT
            grn.xgrnnum,
            grn.xdate,
            grn.xsup,
            s.xorg AS supplier_name,
            grn.xproj,
            grn.xwh,
            grn.xrem,
            grn.xdisc,
            grn.xdtwotax,
            grn.xdtdisc,
            grn.xdttax,
            grn.xval,
            grn.xdiscamt,
            grn.xtotamt,
            grn.xstatusgrn,
            grn.xpornum
        FROM pogrn grn
        LEFT JOIN casup s ON s.zid = grn.zid AND s.xsup = grn.xsup
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
            d.xrate,
            d.xlineamt
        FROM pogdt d
        LEFT JOIN caitem i ON i.zid = d.zid AND i.xitem = d.xitem
        WHERE d.zid = %s AND d.xgrnnum = %s
        ORDER BY d.xrow
    """

    with connection.cursor() as cursor:
        cursor.execute(header_sql, [zid, transaction_id])
        hr = cursor.fetchone()
        if not hr:
            return JsonResponse({'success': False, 'message': 'GRN not found'}, status=404)

        header = {
            'xgrnnum': hr[0],
            'xdate': hr[1].strftime('%Y-%m-%d') if hr[1] else '',
            'xsup': hr[2],
            'supplier_name': hr[3] or '',
            'xproj': hr[4] or '',
            'xwh': hr[5] or '',
            'xrem': hr[6] or '',
            'xdisc': float(hr[7]) if hr[7] is not None else 0.0,
            'xdtwotax': float(hr[8]) if hr[8] is not None else 0.0,
            'xdtdisc': float(hr[9]) if hr[9] is not None else 0.0,
            'xdttax': float(hr[10]) if hr[10] is not None else 0.0,
            'xval': float(hr[11]) if hr[11] is not None else 0.0,
            'xdiscamt': float(hr[12]) if hr[12] is not None else 0.0,
            'xtotamt': float(hr[13]) if hr[13] is not None else 0.0,
            'xstatusgrn': hr[14] or '',
            'xpornum': hr[15] or '',
        }

        cursor.execute(details_sql, [zid, transaction_id])
        rows = cursor.fetchall()

    details = []
    for r in rows:
        details.append({
            'xrow': int(r[0]) if r[0] else 0,
            'xitem': r[1] or '',
            'xdesc': r[2] or (r[1] or ''),
            'xunitstk': r[3] or '',
            'xqty': float(r[4]) if r[4] is not None else 0.0,
            'xrate': float(r[5]) if r[5] is not None else 0.0,
            'xlineamt': float(r[6]) if r[6] is not None else 0.0,
        })

    return JsonResponse({'success': True, 'header': header, 'details': details})


@login_required
@csrf_protect
@require_http_methods(["POST"])
@transaction.atomic
def po_grn_update(request, transaction_id: str):
    zid = request.session.get('current_zid')
    if not zid:
        return JsonResponse({'success': False, 'message': 'Session ZID not found'}, status=401)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    header_data = data.get('header', {})
    details_data = data.get('details', [])
    if not details_data:
        return JsonResponse({'success': False, 'message': 'No details provided'}, status=400)

    def to_decimal(val, default=Decimal('0.00')):
        try:
            return Decimal(str(val))
        except (ValueError, TypeError):
            return default

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT xgrnnum, xdate, xwh, xsup, xproj, xstatusgrn, xpornum
            FROM pogrn WHERE zid = %s AND xgrnnum = %s FOR UPDATE
            """,
            [zid, transaction_id]
        )
        grn_row = cursor.fetchone()
        if not grn_row:
            return JsonResponse({'success': False, 'message': 'GRN not found'}, status=404)
        xgrnnum, xdate, xwh, xsup, xproj, xstatusgrn, xpornum = grn_row
        if str(xstatusgrn) != '1-Open':
            return JsonResponse({'success': False, 'message': 'GRN not open for edit'}, status=409)

        xdate_new = header_data.get('xdate') or (xdate.strftime('%Y-%m-%d') if xdate else None)
        xwh_new = header_data.get('xwh') or xwh
        xproj_new = header_data.get('xproj') or xproj
        xrem_new = header_data.get('xrem', '')
        xdisc_new = to_decimal(header_data.get('xdisc', 0))
        xdtdisc_new = to_decimal(header_data.get('xdtdisc', 0))

        total_amount = Decimal('0.00')
        for item in details_data:
            qty = to_decimal(item.get('xqty', item.get('xqtygrn', 0)))
            rate = to_decimal(item.get('xrate', 0))
            total_amount += (qty * rate)

        percent_disc_amt = (total_amount * xdisc_new) / Decimal('100.0')
        xdiscamt_new = percent_disc_amt + xdtdisc_new
        xtotamt_new = total_amount - xdiscamt_new

        cursor.execute(
            """
            UPDATE pogrn
            SET xdate = %s, xwh = %s, xproj = %s, xrem = %s,
                xdisc = %s, xdtwotax = %s, xdtdisc = %s, xdttax = %s,
                xval = %s, xdiscamt = %s, xtotamt = %s, zutime = %s
            WHERE zid = %s AND xgrnnum = %s
            """,
            [
                xdate_new,
                xwh_new,
                xproj_new,
                xrem_new,
                float(xdisc_new),
                float(total_amount),
                float(xdtdisc_new),
                0.00,
                float(total_amount),
                float(xdiscamt_new),
                float(xtotamt_new),
                timezone.now(),
                zid,
                transaction_id,
            ]
        )

        cursor.execute("DELETE FROM pogdt WHERE zid = %s AND xgrnnum = %s", [zid, transaction_id])

        row_num = 1
        for item in details_data:
            item_code = item.get('xitem')
            qty = to_decimal(item.get('xqty', item.get('xqtygrn', 0)))
            rate = to_decimal(item.get('xrate', 0))
            line_amt = qty * rate

            cursor.execute(
                """
                INSERT INTO pogdt (
                    ztime, zutime, zid, xgrnnum, xrow, xcode, xcodebasis, xitem,
                    xstype, xwh, xdropship, xqty, xqtygrn, xpornum, xcfpur, xwtunit,
                    xcur, xrate, xdisc, xdiscf, xcomm, xexch, xpricebasis, xexchbuy,
                    xprice, xdatesch, xdaterec, xstatusgdt, xtaxrate1, xtaxrate2, xtaxrate3,
                    xtaxrate4, xtaxrate5, xlandcost, xdttax, xdtdisc, xdtwotax, xlineamt,
                    xqtycrn, xchgapply
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s
                )
                """,
                [
                    timezone.now(),
                    timezone.now(),
                    zid,
                    transaction_id,
                    row_num,
                    item_code,
                    'Our Code',
                    item_code,
                    'Stock-N-Sell',
                    xwh_new,
                    0,
                    float(qty),
                    float(qty),
                    xpornum,
                    1.000000,
                    0.000,
                    'BDT',
                    float(rate),
                    0.00,
                    0.00,
                    0.00,
                    1.0000000000,
                    'Entered',
                    0.0000000000,
                    float(rate),
                    '2999-12-31',
                    xdate_new,
                    '1-Open',
                    0.0000,
                    0.0000,
                    0.0000,
                    0.0000,
                    0.0000,
                    0.000,
                    0.00,
                    0.00,
                    float(line_amt),
                    float(line_amt),
                    0.000,
                    'Yes',
                ]
            )
            row_num += 1

    return JsonResponse({'success': True, 'message': 'GRN updated', 'grn': transaction_id})


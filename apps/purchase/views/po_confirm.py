from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.db import connection, transaction
from django.utils import timezone
from decimal import Decimal
from apps.utils.voucher_generator import generate_voucher_number
import logging

logger = logging.getLogger(__name__)

@login_required
@csrf_protect
@require_http_methods(["POST"])
def po_confirm(request, transaction_id: str):
    try:
        zid = request.session.get('current_zid') or 100001
        if not transaction_id:
            return JsonResponse({'success': False, 'message': 'Invalid transaction ID'}, status=400)

        session_user = getattr(request.user, 'username', '') or getattr(request.user, 'email', '') or 'system'
        now_ts = timezone.now()

        def get_avg_price(item_code: str) -> Decimal:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(xval * xsign), 0), COALESCE(SUM(xqty * xsign), 0)
                    FROM imtrn WHERE zid = %s AND xitem = %s
                    """,
                    [zid, item_code]
                )
                row = cursor.fetchone() or (Decimal('0'), Decimal('0'))
            total_val = Decimal(str(row[0]))
            total_qty = Decimal(str(row[1]))
            if total_qty == 0:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT COALESCE(xstdcost, 0) FROM caitem WHERE zid = %s AND xitem = %s",
                        [zid, item_code]
                    )
                    r = cursor.fetchone()
                    return Decimal(str(r[0])) if r and r[0] is not None else Decimal('0')
            return (total_val / total_qty).quantize(Decimal('0.000000'))

        with transaction.atomic():
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
                    return JsonResponse({'success': False, 'message': 'GRN already processed'}, status=409)

                year = (xdate.strftime('%Y') if xdate else now_ts.strftime('%Y'))
                month = (xdate.strftime('%m') if xdate else now_ts.strftime('%m'))

                cursor.execute(
                    """
                    SELECT xitem, xqty, xrate
                    FROM pogdt WHERE zid = %s AND xgrnnum = %s ORDER BY xrow
                    """,
                    [zid, transaction_id]
                )
                items = cursor.fetchall()

                if not items:
                    return JsonResponse({'success': False, 'message': 'No items to confirm for GRN'}, status=400)

                for idx, (xitem, xqty, xrate) in enumerate(items, start=1):
                    qty = Decimal(str(xqty or 0))
                    avg_price = get_avg_price(str(xitem))
                    if avg_price == 0:
                        avg_price = Decimal(str(xrate or 0))
                    xval = (qty * avg_price).quantize(Decimal('0.000000'))

                    im_voucher = generate_voucher_number(zid=zid, prefix='RE--', table='imtrn', column='ximtrnnum')

                    cursor.execute(
                        """
                        INSERT INTO imtrn (
                            ztime, zid, ximtrnnum, xitem, xwh, xdate, xyear, xper,
                            xqty, xval, xvalpost, xdoctype, xdocnum, xdocrow, xnote,
                            xaltqty, xsec, xproj, xdateexp, xdaterec, xsup, xaction,
                            xsign, xtime, zemail, xtrnim, xmember
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s
                        )
                        """,
                        [
                            now_ts,
                            zid,
                            im_voucher,
                            str(xitem),
                            str(xwh),
                            xdate,
                            str(year),
                            str(month),
                            f"{float(qty):.3f}",
                            f"{float(xval):.6f}",
                            f"{float(xval):.6f}",
                            '0027',
                            str(xgrnnum),
                            int(idx),
                            'Goods Received',
                            '0.000',
                            'Any',
                            str(xproj or ''),
                            xdate,
                            xdate,
                            str(xsup or ''),
                            'Receipt',
                            '1',
                            now_ts,
                            session_user,
                            'RE--',
                            session_user,
                        ]
                    )

                cursor.execute(
                    "UPDATE pogrn SET xstatusgrn = '5-Confirmed' WHERE zid = %s AND xgrnnum = %s",
                    [zid, transaction_id]
                )
                cursor.execute(
                    "UPDATE pogdt SET xstatusgdt = '5-Confirmed' WHERE zid = %s AND xgrnnum = %s",
                    [zid, transaction_id]
                )

        logger.info(f"GRN {transaction_id} confirmed by {session_user}")
        return JsonResponse({'success': True, 'grn': transaction_id})

    except Exception as e:
        logger.error(f"Error confirming GRN {transaction_id}: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Failed to confirm GRN', 'details': str(e)}, status=500)

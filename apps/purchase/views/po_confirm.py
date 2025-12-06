from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.db import connection, transaction
from django.utils import timezone
import re
from decimal import Decimal
from apps.utils.voucher_generator import generate_voucher_number, generate_sinv_voucher
from apps.utils.average_price_calculation import get_average_price
import logging

logger = logging.getLogger(__name__)

@login_required
@csrf_protect
@require_http_methods(["POST"])
def po_confirm(request, transaction_id: str):
    """Confirm a GRN: posts inventory receipts (imtrn) and marks GRN lines/status as confirmed.
    Steps:
    - Validate context and input
    - Lock GRN header; ensure it is open
    - Load GRN detail lines
    - Compute average price per item via shared utility (fallback to line rate)
    - Insert corresponding inventory receipt transactions
    - Update GRN header and detail statuses
    - Return JSON response
    """
    try:
        # Resolve business context (zid); default to 100001 if session missing
        zid = request.session.get('current_zid') or 100001
        if not transaction_id:
            # Reject when transaction id is not provided
            return JsonResponse({'success': False, 'message': 'Invalid transaction ID'}, status=400)

        # Resolve user identity for audit columns
        session_user = getattr(request.user, 'username', '') or getattr(request.user, 'email', '') or 'system'
        # Current timestamp used for ztime/xtime and fallbacks
        now_ts = timezone.now()

        # Begin atomic transaction to ensure consistency
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Lock GRN header row; ensure it belongs to current zid
                cursor.execute(
                    """
                    SELECT xgrnnum, xdate, xwh, xsup, xproj, xstatusgrn, xpornum
                    FROM pogrn WHERE zid = %s AND xgrnnum = %s FOR UPDATE
                    """,
                    [zid, transaction_id]
                )
                grn_row = cursor.fetchone()
                if not grn_row:
                    # GRN header not found
                    return JsonResponse({'success': False, 'message': 'GRN not found'}, status=404)
                xgrnnum, xdate, xwh, xsup, xproj, xstatusgrn, xpornum = grn_row
                if str(xstatusgrn) != '1-Open':
                    # Only open GRNs can be processed
                    return JsonResponse({'success': False, 'message': 'GRN already processed'}, status=409)

                # Derive posting year/month from GRN date (fallback to now)
                year = (xdate.strftime('%Y') if xdate else now_ts.strftime('%Y'))
                month = (xdate.strftime('%m') if xdate else now_ts.strftime('%m'))

                # Load GRN detail lines to post
                cursor.execute(
                    """
                    SELECT xitem, xqty, xrate, xlineamt
                    FROM pogdt WHERE zid = %s AND xgrnnum = %s ORDER BY xrow
                    """,
                    [zid, transaction_id]
                )
                items = cursor.fetchall()

                if not items:
                    # No lines to process
                    return JsonResponse({'success': False, 'message': 'No items to confirm for GRN'}, status=400)

                total_line_amount = Decimal('0.00')
                ledger_rows = []

                for idx, (xitem, xqty, xrate, xlineamt) in enumerate(items, start=1):
                    # Quantity to receive
                    qty = Decimal(str(xqty or 0))
                    # Average price via shared utility (bounded to GRN date)
                    avg_price_float = get_average_price(
                        zid,
                        str(xitem),
                        (xdate.strftime('%Y-%m-%d') if xdate else now_ts.strftime('%Y-%m-%d'))
                    )

                    # Accumulate total line amount and collect ledger rows
                    line_amount = Decimal(str(xlineamt or 0)) if xlineamt is not None else (qty * Decimal(str(xrate or 0)))
                    total_line_amount += line_amount
                    ledger_rows.append((idx, line_amount))
                    avg_price = Decimal(str(avg_price_float))
                    # Fallback to GRN line rate when average price is zero
                    if avg_price == Decimal('0'):
                        avg_price = Decimal(str(xrate or 0))
                    # Extended value for this receipt line
                    xval = (qty * avg_price).quantize(Decimal('0.000000'))

                    # Generate inventory receipt voucher number for imtrn
                    im_voucher = generate_voucher_number(zid=zid, prefix='RE--', table='imtrn', column='ximtrnnum')

                    # Post inventory receipt line into imtrn
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
                            %s, %s, %s, %s, %s
                        )
                        """,
                        [
                            now_ts,              # ztime
                            zid,                 # zid
                            im_voucher,          # ximtrnnum
                            str(xitem),          # xitem
                            str(xwh),            # xwh
                            xdate,               # xdate
                            str(year),           # xyear
                            str(month),          # xper
                            f"{float(qty):.3f}",  # xqty
                            f"{float(xval):.6f}", # xval
                            f"{float(xval):.6f}", # xvalpost
                            '0027',              # xdoctype
                            str(xgrnnum),        # xdocnum
                            int(idx),            # xdocrow
                            'Goods Received',    # xnote
                            '0.000',             # xaltqty
                            'Any',               # xsec
                            str(xproj or ''),    # xproj
                            xdate,               # xdateexp
                            xdate,               # xdaterec
                            str(xsup or ''),     # xsup
                            'Receipt',           # xaction
                            '1',                 # xsign
                            now_ts,              # xtime
                            session_user,        # zemail
                            'RE--',              # xtrnim
                            session_user,        # xmember
                        ]
                    )

                # Generate supplier invoice voucher and insert GL header (after IM postings)
                sinv_voucher = generate_sinv_voucher(zid=zid, prefix='SINV')
                xlong = f"**System generated Supplier Invoice** MRR Number: {xgrnnum}"
                cursor.execute(
                    """
                    INSERT INTO glheader (
                        ztime, zid, xvoucher, xref, xdate, xlong, xpostflag,
                        xyear, xper, xstatusjv, xdatedue, xdesc05, dumzid, zemail,
                        xnumofper, xtrngl, xnote, xmember, xaction
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    """,
                    [
                        now_ts,              # ztime
                        zid,                 # zid
                        sinv_voucher,        # xvoucher
                        str(xgrnnum),        # xref
                        xdate,               # xdate
                        xlong,               # xlong
                        'Posted',            # xpostflag
                        str(year),           # xyear
                        str(month),          # xper
                        'Balanced',          # xstatusjv
                        xdate,               # xdatedue
                        str(xgrnnum),        # xdesc05
                        0,                   # dumzid
                        session_user,        # zemail
                        0,                   # xnumofper
                        'SINV',              # xtrngl
                        xlong,               # xnote
                        session_user,        # xmember
                        'Journal',           # xaction
                    ]
                )

                # Insert GL Detail (Ledger) rows for each item
                ledger_account = "01060003" if str(zid) == "100001" else "1060003"
                for row_idx, line_amount in ledger_rows:
                    cursor.execute(
                        """
                        INSERT INTO gldetail (
                            ztime, zutime, zid, xvoucher, xrow, xacc, xaccusage, xaccsource,
                            xsec, xproj, xcur, xexch, xprime, xbase, xacctype, zemail, xamount,
                            xallocation, xdateapp, xexchval, xdateclr, xdatedue
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s
                        )
                        """,
                        [
                            now_ts,                # ztime
                            None,                  # zutime
                            zid,                   # zid
                            sinv_voucher,          # xvoucher
                            int(row_idx),          # xrow
                            ledger_account,        # xacc
                            'Ledger',              # xaccusage
                            'None',                # xaccsource
                            'Any',                 # xsec
                            str(xproj or ''),      # xproj
                            'BDT',                 # xcur
                            1.0000000000,          # xexch
                            float(line_amount),    # xprime
                            float(line_amount),    # xbase
                            'Liability',           # xacctype
                            session_user,          # zemail
                            float(line_amount),    # xamount
                            Decimal('0.00'),       # xallocation
                            xdate,                 # xdateapp
                            0.0000000000,          # xexchval
                            xdate,                 # xdateclr
                            xdate,                 # xdatedue
                        ]
                    )

                # Insert single GL Detail row for Accounts Payable
                ap_account = "09030001" if str(zid) == "100001" else "9030001"
                ap_row_number = 40
                ap_prime = -float(total_line_amount)
                ap_base = -float(total_line_amount)
                ap_amount = float(total_line_amount)
                # Derive numeric part for xinvnum from GRN number
                grn_numeric = re.sub(r"\D", "", str(xgrnnum)) if xgrnnum else ""
                cursor.execute(
                    """
                    INSERT INTO gldetail (
                        ztime, zutime, zid, xvoucher, xrow, xacc, xaccusage, xaccsource,
                        xsub, xsec, xproj, xcur, xexch, xprime, xbase, xacctype, zemail,
                        xamount, xallocation, xinvnum, xoriginal, xdateapp, xexchval, xdateclr, xdatedue
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    [
                        now_ts,               # ztime
                        None,                 # zutime
                        zid,                  # zid
                        sinv_voucher,         # xvoucher
                        ap_row_number,        # xrow
                        ap_account,           # xacc
                        'AP',                 # xaccusage
                        'Supplier',           # xaccsource
                        str(xsup or ''),      # xsub
                        'Any',                # xsec
                        str(xproj or ''),     # xproj
                        'BDT',                # xcur
                        1.0000000000,         # xexch
                        ap_prime,             # xprime
                        ap_base,              # xbase
                        'Liability',          # xacctype
                        session_user,         # zemail
                        ap_amount,            # xamount
                        Decimal('0.00'),      # xallocation
                        grn_numeric,          # xinvnum
                        str(xgrnnum),         # xoriginal
                        xdate,                # xdateapp
                        0.0000000000,         # xexchval
                        xdate,                # xdateclr
                        xdate,                # xdatedue
                    ]
                )

                # Update PO header with received status, GRN number, and SINV reference
                cursor.execute(
                    """
                    UPDATE poord
                    SET xstatuspor = '5-Received', xgrnnum = %s, xref = %s
                    WHERE zid = %s AND xpornum = %s
                    """,
                    [xgrnnum, sinv_voucher, zid, xpornum]
                )

                # Mark GRN header as confirmed
                cursor.execute(
                    "UPDATE pogrn SET xstatusgrn = '5-Confirmed', xstatusqc = '8-QC Completed', xref = %s, xsinnum = %s WHERE zid = %s AND xgrnnum = %s",
                    [sinv_voucher, grn_numeric, zid, transaction_id]
                )
                # Mark GRN detail lines as confirmed
                cursor.execute(
                    "UPDATE pogdt SET xstatusgdt = '5-Confirmed' WHERE zid = %s AND xgrnnum = %s",
                    [zid, transaction_id]
                )

        # Log confirmation and respond
        logger.info(f"GRN {transaction_id} confirmed by {session_user}")
        return JsonResponse({'success': True, 'grn': transaction_id})

    except Exception as e:
        # Generic error handling for any failure during confirmation
        logger.error(f"Error confirming GRN {transaction_id}: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Failed to confirm GRN', 'details': str(e)}, status=500)

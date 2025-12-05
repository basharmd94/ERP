# Standard library imports
import json
import logging
from decimal import Decimal
# Django imports
from django.db import transaction, connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Local application imports
from apps.utils.voucher_generator import generate_voucher_number

# Set up logging
logger = logging.getLogger(__name__)


@csrf_exempt
@transaction.atomic
@login_required
def po_create(request):
    """
    API endpoint to create a Purchase Order.
    Expects JSON data with 'header' and 'details' keys.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST method is allowed'}, status=405)

    try:
        # Parse JSON data
        data = json.loads(request.body)
        header_data = data.get('header', {})
        details_data = data.get('details', [])

        if not header_data or not details_data:
            return JsonResponse({'success': False, 'message': 'Missing header or details data'}, status=400)

        # Get session data
        current_zid = request.session.get('current_zid')
        session_user_email = request.user.email

        if not current_zid:
             return JsonResponse({'success': False, 'message': 'Session ZID not found'}, status=401)

        # 1. Generate Voucher Number for PO
        # Using prefix from frontend or default 'PO--'
        prefix = 'PO--'

        voucher_number = generate_voucher_number(
            zid=current_zid,
            prefix=prefix,
            table='poord',
            column='xpornum',
            length=6 # Assuming 6 digit sequence
        )

        if not voucher_number:
             return JsonResponse({'success': False, 'message': 'Failed to generate voucher number'}, status=500)

        # Current timestamp
        current_timestamp = timezone.now()

        # 2. Prepare Header Data (poord)
        # Map frontend fields to database columns based on user requirement

        # Safe Decimal conversion helper
        def to_decimal(val, default=Decimal('0.00')):
             try:
                 return Decimal(str(val))
             except (ValueError, TypeError):
                 return default

        xdate = header_data.get('xdate') # Required
        xsup = header_data.get('xsup') # Required
        xproj = header_data.get('xproj') # Required
        xwh = header_data.get('xwh') # Required
        xrem = header_data.get('xrem', '')

        # Amounts
        # xdisc is percent discount from frontend
        xdisc_percent = to_decimal(header_data.get('xdisc', 0))
        # xdtdisc is fixed discount from frontend
        xdtdisc_fixed = to_decimal(header_data.get('xdtdisc', 0))

        # Total amount of cart (before discount) - xdtwotax, xval, xtotamt seem to share base value in example
        # In example: "xdtwotax": "73727.00" -- total amount of cart
        # We should calculate this from details to be safe, or trust frontend.
        # Trusting frontend for now as per typical pattern, but verifying sum is better practice.
        # For this implementation, I will sum detail line amounts for xdtwotax/xval/xtotamt base.

        calculated_total_cart_amount = Decimal('0.00')
        for item in details_data:
             qty = to_decimal(item.get('xqtyord', 0))
             rate = to_decimal(item.get('xrate', 0))
             calculated_total_cart_amount += (qty * rate)

        xdtwotax = calculated_total_cart_amount
        xval = calculated_total_cart_amount

        # Discount amount calculation
        # xdiscamt = (Total * Percent / 100) + Fixed
        percent_disc_amt = (calculated_total_cart_amount * xdisc_percent) / Decimal('100.0')
        xdiscamt = percent_disc_amt + xdtdisc_fixed

        xtotamt = calculated_total_cart_amount - xdiscamt

        # Insert into poord
        poord_sql = """
            INSERT INTO poord (
                ztime, zid, xpornum, xdate, xsup, xsupref, xdatesupref,
                xdiv, xsec, xproj, xstatuspor, xappamt, xpartial,
                xcur, xexch, xrem, xwh, xdisc, xdtwotax, xdtdisc,
                xdttax, xval, xdiscamt, xtotamt, zemail, xemail,
                xtrnpor, xtypepor, xwhoption, xmember
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """

        poord_values = [
            current_timestamp,          # ztime
            current_zid,                # zid
            voucher_number,             # xpornum
            xdate,                      # xdate
            xsup,                       # xsup
            header_data.get('xsupref', ''), # xsupref
            xdate,                      # xdatesupref (using xdate as default per example logic or input)
            header_data.get('xdiv', ''), # xdiv
            header_data.get('xsec', 'Any'), # xsec
            xproj,                      # xproj
            '1-Open',                   # xstatuspor
            0.00,                       # xappamt
            0,                          # xpartial
            'BDT',                      # xcur
            1.0000000000,               # xexch
            xrem,                       # xrem
            xwh,                        # xwh
            xdisc_percent,              # xdisc (percent)
            xdtwotax,                   # xdtwotax
            xdtdisc_fixed,              # xdtdisc (fixed)
            0.00,                       # xdttax
            xval,                       # xval
            xdiscamt,                   # xdiscamt
            xtotamt,                    # xtotamt
            session_user_email,         # zemail
            session_user_email,         # xemail
            prefix,                     # xtrnpor
            'Local',                    # xtypepor
            'Header',                   # xwhoption
            session_user_email          # xmember
        ]

        with connection.cursor() as cursor:
            cursor.execute(poord_sql, poord_values)

            # 3. Prepare Detail Data (poodt)
            poodt_sql = """
                INSERT INTO poodt (
                    ztime, zid, xpornum, xrow, xcode, xcodebasis, xitem,
                    xstatuspdt, xstype, xwh, xdropship, xqtyord, xqtygrn,
                    xqtystk, xcfpur, xwtunit, xcur, xexch, xrate, xmargin,
                    xdisc, xdiscf, xcomm, xpricebasis, xexchbuy, xprice,
                    xdatesch, xtaxrate1, xtaxrate2, xtaxrate3, xtaxrate4,
                    xtaxcode5, xtaxrate5, xlandcost, xdttax, xdtdisc,
                    xdtwotax, xlineamt, xline, xcompwh
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
            """

            row_num = 1
            for item in details_data:
                item_code = item.get('xitem')
                qty = to_decimal(item.get('xqtyord', 0))
                rate = to_decimal(item.get('xrate', 0))
                line_amt = qty * rate

                poodt_values = [
                    current_timestamp,      # ztime
                    current_zid,            # zid
                    voucher_number,         # xpornum
                    row_num,                # xrow
                    item_code,              # xcode
                    'Our Code',             # xcodebasis
                    item_code,              # xitem
                    'Priced',               # xstatuspdt
                    'Stock-N-Sell',         # xstype
                    xwh,                    # xwh (from header)
                    0,                      # xdropship
                    qty,                    # xqtyord
                    qty,                    # xqtygrn
                    0.000,                  # xqtystk
                    1.000000,               # xcfpur
                    0.000,                  # xwtunit
                    'BDT',                  # xcur
                    1.0000000000,           # xexch
                    rate,                   # xrate
                    0.00,                   # xmargin
                    0.00,                   # xdisc
                    0.00,                   # xdiscf
                    0.00,                   # xcomm
                    'Entered',              # xpricebasis
                    0.0000000000,           # xexchbuy
                    rate,                   # xprice
                    '2999-12-31',           # xdatesch
                    0.0000,                 # xtaxrate1
                    0.0000,                 # xtaxrate2
                    0.0000,                 # xtaxrate3
                    0.0000,                 # xtaxrate4
                    '',                     # xtaxcode5
                    0.0000,                 # xtaxrate5
                    0.000,                  # xlandcost
                    0.00,                   # xdttax
                    0.00,                   # xdtdisc
                    line_amt,               # xdtwotax
                    line_amt,               # xlineamt
                    0,                      # xline
                    xwh                     # xcompwh
                ]

                cursor.execute(poodt_sql, poodt_values)
                row_num += 1

            grn_prefix = 'GRN-'
            grn_number = generate_voucher_number(
                zid=current_zid,
                prefix=grn_prefix,
                table='pogrn',
                column='xgrnnum',
                length=6
            )

            if not grn_number:
                return JsonResponse({'success': False, 'message': 'Failed to generate GRN number'}, status=500)

            grn_without_prefix = grn_number[len(grn_prefix):] if grn_number.startswith(grn_prefix) else grn_number

            pogrn_sql = """
                INSERT INTO pogrn (
                    ztime, zutime, zid, xgrnnum, xdate, xpornum, xshiplno, xrow, xsinnum,
                    xsup, xsupref, xdatesupref, xdatedue, xsec, xproj, xstatusgrn, xcur,
                    xexch, xwh, xrem, xdisc, xdtwotax, xdtdisc, xdttax, xval, xdiscamt,
                    xtotamt, zemail, xstatusqc, xtypepor, xwhoption, xmember, xconfirmt,
                  xfailedt,  xreviset,  xinvoicet, xdiscf
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """

            pogrn_values = [
                current_timestamp,          # ztime
                timezone.now(),             # zutime
                current_zid,                # zid
                grn_number,                 # xgrnnum
                xdate,                      # xdate
                voucher_number,             # xpornum
                '0',                        # xshiplno
                0,                          # xrow
                grn_without_prefix,         # xsinnum
                xsup,                       # xsup
                header_data.get('xsupref', ''),  # xsupref
                xdate,                      # xdatesupref
                xdate,                      # xdatedue
                'Any',                      # xsec
                xproj,                      # xproj
                '1-Open',                   # xstatusgrn
                'BDT',                      # xcur
                1.0000000000,               # xexch
                xwh,                        # xwh
                xrem,                       # xrem
                xdisc_percent,              # xdisc
                xdtwotax,                   # xdtwotax
                xdtdisc_fixed,              # xdtdisc
                0.00,                       # xdttax
                xval,                       # xval
                xdiscamt,                   # xdiscamt
                xtotamt,                    # xtotamt
                session_user_email,         # zemail
                '1-Open',                   # xstatusqc
                'Local',                    # xtypepor
                'Header',                   # xwhoption
                session_user_email,         # xmember
                timezone.now(),             # xconfirmt
                timezone.now(),             # xfailedt
                timezone.now(),             # xreviset
                timezone.now(),             # xinvoicet
                0                           # xdiscf
            ]

            cursor.execute(pogrn_sql, pogrn_values)

            pogdt_sql = """
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
            """

            row_num = 1
            for item in details_data:
                item_code = item.get('xitem')
                qty = to_decimal(item.get('xqtyord', 0))
                rate = to_decimal(item.get('xrate', 0))
                line_amt = qty * rate

                pogdt_values = [
                    current_timestamp,      # ztime
                    timezone.now(),         # zutime
                    current_zid,            # zid
                    grn_number,             # xgrnnum
                    row_num,                # xrow
                    item_code,              # xcode
                    'Our Code',             # xcodebasis
                    item_code,              # xitem
                    'Stock-N-Sell',         # xstype
                    xwh,                    # xwh
                    0,                      # xdropship
                    qty,                    # xqty
                    qty,                    # xqtygrn
                    voucher_number,         # xpornum
                    1.000000,               # xcfpur
                    0.000,                  # xwtunit
                    'BDT',                  # xcur
                    rate,                   # xrate
                    0.00,                   # xdisc
                    0.00,                   # xdiscf
                    0.00,                   # xcomm
                    1.0000000000,           # xexch
                    'Entered',              # xpricebasis
                    0.0000000000,           # xexchbuy
                    rate,                   # xprice
                    '2999-12-31',           # xdatesch
                    xdate,                  # xdaterec
                    '1-Open',               # xstatusgdt
                    0.0000,                 # xtaxrate1
                    0.0000,                 # xtaxrate2
                    0.0000,                 # xtaxrate3
                    0.0000,                 # xtaxrate4
                    0.0000,                 # xtaxrate5
                    0.000,                  # xlandcost
                    0.00,                   # xdttax
                    0.00,                   # xdtdisc
                    line_amt,               # xdtwotax
                    line_amt,               # xlineamt
                    0.000,                  # xqtycrn
                    'Yes'                   # xchgapply
                ]

                cursor.execute(pogdt_sql, pogdt_values)
                row_num += 1

        return JsonResponse({
            'success': True,
            'message': 'Purchase Order created successfully',
            'voucher_number': voucher_number,
            'grn_number': grn_number
        })

    except Exception as e:
        logger.error(f"Error creating Purchase Order: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

# Standard library imports
import json
import logging
from datetime import datetime
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
def sales_return_confirm(request):
    """
    AJAX endpoint to confirm a sales return with inventory validation
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        logger.info(f"Received sales return data: {data}")

        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({
                'success': False,
                'error': 'No business context found'
            }, status=400)

        # Extract form data
        form_data = data.get('formData', {})
        cart_items = data.get('cartItems', [])

        if not cart_items:
            return JsonResponse({
                'success': False,
                'error': 'No items in cart'
            }, status=400)

        # Validate required fields
        required_fields = ['invoice_date', 'receive_type', 'supplier_select', 'warehouse', 'project']
        for field in required_fields:
            if not form_data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)

        # Generate voucher numbers
        sre_voucher = generate_voucher_number(
            zid=current_zid,
            prefix='SRE-',
            table='imtemptrn',
            column='ximtmptrn'
        )

        sret_voucher = generate_voucher_number(
            zid=current_zid,
            prefix='SRET',
            table='glheader',
            column='xvoucher'
        )

        current_timestamp = timezone.now()
        session_user = request.user.username
        invoice_date = form_data['invoice_date']

        # Parse date for year and month
        date_obj = datetime.strptime(invoice_date, '%Y-%m-%d')
        year = date_obj.year
        month = f"{date_obj.month:02d}"

        # Get totals from frontend (already calculated)
        totals = data.get('totals', {})
        total_market_value = Decimal(str(totals.get('totalMktValue', 0)))
        total_inventory_value = Decimal(str(totals.get('totalInvValue', 0)))

        with connection.cursor() as cursor:
            # 1. Insert into imtemptrn
            cursor.execute("""
                INSERT INTO imtemptrn (
                    ztime, zid, ximtmptrn, xref, xdate, xproj, xwh, xglref, xsup, xcus,
                    xstatustrn, xyear, xper, xsign, xaction, zemail
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                current_timestamp,  # ztime
                current_zid,  # zid
                sre_voucher,  # ximtmptrn
                form_data.get('notes', f'Sales Return - {sre_voucher}'),  # xref
                invoice_date,  # xdate
                form_data['project'],  # xproj
                form_data['warehouse'],  # xwh
                sret_voucher,  # xglref
                form_data['supplier_select'],  # xsup
                '',  # xcus (empty for sales return)
                '5-Confirmed',  # xstatustrn
                year,  # xyear
                month,  # xper
                1,  # xsign (positive for return)
                'Sales Return',  # xaction
                session_user  # zemail
            ])

            # 2. Insert into imtemptdt and imtrn for each cart item
            for idx, item in enumerate(cart_items, 1):
                # Generate individual voucher for each item
                item_voucher = generate_voucher_number(current_zid, 'SRE-', 'imtemptdt', 'ximtrnnum')

                inv_value = Decimal(str(item.get('mkt_price', 0)))
                item_total = Decimal(str(item.get('quantity', 0))) * inv_value
                mkt_value = Decimal(str(item.get('quantity', 0))) * Decimal(str(item.get('xstdprice', item.get('mkt_price', 0))))

                # Insert into imtemptdt
                cursor.execute("""
                    INSERT INTO imtemptdt (
                        ztime, zutime, zid, ximtmptrn, xtorlno, xitem, xqtyord, xunit,
                        ximtrnnum, xrate, xval, zemail, xqtyreq, xdatesch, xfrslnum,
                        xtoslnum, xstdprice, xlineamt
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, [
                    current_timestamp,  # ztime
                    current_timestamp,  # zutime
                    current_zid,  # zid
                    sre_voucher,  # ximtmptrn (main voucher)
                    idx,  # xtorlno (serial number)
                    item['xitem'],  # xitem
                    Decimal(str(item.get('quantity', 0))),  # xqtyord
                    item.get('xunitstk', 'Pcs'),  # xunit
                    item_voucher,  # ximtrnnum (individual item voucher)
                    inv_value,  # xrate (INV Value)
                    item_total,  # xval (INV Value total)
                    session_user,  # zemail
                    Decimal(str(item.get('quantity', 0))),  # xqtyreq
                    '2999-12-31',  # xdatesch (default)
                    0,  # xfrslnum (default 0)
                    0,  # xtoslnum (default 0)
                    Decimal(str(item.get('xstdprice', item.get('mkt_price', 0)))),  # xstdprice
                    mkt_value  # xlineamt (MKT Value)
                ])

                # Insert into imtrn
                item_total = Decimal(str(item.get('quantity', 0))) * Decimal(str(item.get('mkt_price', 0)))
                cursor.execute("""
                    INSERT INTO imtrn (
                        ztime, zid, ximtrnnum, xitem, xwh, xdate, xyear, xper, xqty, xval,
                        xvalpost, xdoctype, xdocnum, xdocrow, xaltqty, xproj, xdateexp,
                        xdaterec, xaction, xsign, xmember
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, [
                    current_timestamp,  # ztime
                    current_zid,  # zid
                    item_voucher,  # ximtrnnum (individual item voucher)
                    item['xitem'],  # xitem
                    form_data['warehouse'],  # xwh
                    invoice_date,  # xdate
                    year,  # xyear
                    month,  # xper
                    Decimal(str(item.get('quantity', 0))),  # xqty
                    item_total,  # xval
                    item_total,  # xvalpost (same as xval)
                    'SRE-',  # xdoctype
                    sre_voucher,  # xdocnum
                    str(idx),  # xdocrow (row number as string)
                    0,  # xaltqty (default 0)
                    form_data['project'],  # xproj
                    invoice_date,  # xdateexp
                    invoice_date,  # xdaterec
                    'Return',  # xaction
                    1,  # xsign (default 1)
                    session_user  # xmember
                ])

            # 4. Insert into glheader
            cursor.execute("""
                INSERT INTO glheader (
                    ztime, zid, xvoucher, xref, xdate, xlong, xpostflag,
                    xyear, xper, xstatusjv, xdatedue, xnumofper, xtrngl,
                    xmember, xapproved, xaction
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                current_timestamp,  # ztime
                current_zid,  # zid
                sret_voucher,  # xvoucher
                f"***System generated Sales Return voucher on {invoice_date}",  # xref
                invoice_date,  # xdate
                f"** Sales Return Created By System On {invoice_date} **",  # xlong
                True,  # xpostflag
                year,  # xyear
                month,  # xper
                "Balanced",  # xstatusjv
                invoice_date,  # xdatedue
                0,  # xnumofper
                "SALE",  # xtrngl
                session_user,  # xmember
                1,  # xapproved
                "Journal"  # xaction
            ])

            # 5. Insert into gldetail
            # Use project directly from form data
            project_code = form_data['project']

            # Account logic based on session ZID and row number
            # Row 1: Sales Account
            if current_zid == "100001":
                row1_account = "08010001"
            else:
                row1_account = "8010001"
            # Row 2: Cash/Bank Account or Accounts Receivable
            if current_zid == "100001":
                row2_account = "01010001"
            elif current_zid == "100002":
                row2_account = "1030001"  # Accounts Receivable for Central Store
            else:
                row2_account = "1010001"

            # Row 3: Inventory Account
            if current_zid == "100001":
                row3_account = "01060003"
            else:
                row3_account = "1060003"

            # Row 4: Cost of Goods Sold Account
            if current_zid == "100001":
                row4_account = "04010020"
            else:
                row4_account = "4010020"

            # Extract customer code from form data for xsub
            customer_code = form_data.get('customer', '')

            # Define xaccusage, xaccsource, and xsub values based on zid
            if current_zid in ["100001", "100003"]:
                # For zid 100001 and 100003
                xaccusage_values = ["Ledger", "Cash", "Ledger", "Ledger"]
                xaccsource_values = ["None", "None", "None", "None"]
                xsub_values = ["", "", "", ""]
            elif current_zid == "100002":
                # For zid 100002
                xaccusage_values = ["Ledger", "AR", "Ledger", "Ledger"]
                xaccsource_values = ["None", "Customer", "None", "None"]
                xsub_values = ["", customer_code, "", ""]
            else:
                # Default fallback
                xaccusage_values = ["Ledger", "Cash", "Ledger", "Ledger"]
                xaccsource_values = ["None", "None", "None", "None"]
                xsub_values = ["", "", "", ""]

            # GL Detail Row 1 - Sales Return (Debit)
            cursor.execute("""
                INSERT INTO gldetail (
                    ztime, zutime, zid, xvoucher, xrow, xacc, xaccusage, xaccsource,
                    xproj, xcur, xexch, xprime, xbase, xacctype, zemail, xamount, xallocation, xsub
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                current_timestamp,  # ztime
                None,  # zutime
                current_zid,  # zid
                sret_voucher,  # xvoucher (Generated voucher from imtemptrn.xglref)
                1,  # xrow
                row1_account,  # xacc
                xaccusage_values[0],  # xaccusage (conditional based on zid)
                xaccsource_values[0],  # xaccsource (conditional based on zid)
                project_code,  # xproj
                "BDT",  # xcur
                1.0000000000,  # xexch
                total_market_value,  # xprime (total MKT Value)
                total_market_value,  # xbase (total MKT Value)
                "Income",  # xacctype
                session_user,  # zemail (logged user)
                total_market_value,  # xamount (total MKT Value - positive)
                Decimal('0.00'),  # xallocation (default 0)
                xsub_values[0]  # xsub (conditional based on zid)
            ])

            # GL Detail Row 2 - Cash/Bank (Credit)
            cursor.execute("""
                INSERT INTO gldetail (
                    ztime, zutime, zid, xvoucher, xrow, xacc, xaccusage, xaccsource,
                    xproj, xcur, xexch, xprime, xbase, xacctype, zemail, xamount, xallocation, xsub
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                current_timestamp,  # ztime
                None,  # zutime
                current_zid,  # zid
                sret_voucher,  # xvoucher (Generated voucher from imtemptrn.xglref)
                2,  # xrow
                row2_account,  # xacc
                xaccusage_values[1],  # xaccusage (conditional based on zid)
                xaccsource_values[1],  # xaccsource (conditional based on zid)
                project_code,  # xproj
                "BDT",  # xcur
                1.0000000000,  # xexch
                -total_market_value,  # xprime (total MKT Value minus figured)
                -total_market_value,  # xbase (total MKT Value minus figured)
                "Asset",  # xacctype
                session_user,  # zemail (logged user)
                total_market_value,  # xamount (total MKT Value - positive)
                Decimal('0.00'),  # xallocation (default 0)
                xsub_values[1]  # xsub (conditional based on zid)
            ])

            # GL Detail Row 3 - Inventory (Debit)
            cursor.execute("""
                INSERT INTO gldetail (
                    ztime, zutime, zid, xvoucher, xrow, xacc, xaccusage, xaccsource,
                    xproj, xcur, xexch, xprime, xbase, xacctype, zemail, xamount, xallocation, xsub
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                current_timestamp,  # ztime
                None,  # zutime
                current_zid,  # zid
                sret_voucher,  # xvoucher (Generated voucher from imtemptrn.xglref)
                3,  # xrow
                row3_account,  # xacc
                xaccusage_values[2],  # xaccusage (conditional based on zid)
                xaccsource_values[2],  # xaccsource (conditional based on zid)
                project_code,  # xproj
                "BDT",  # xcur
                1.0000000000,  # xexch
                total_inventory_value,  # xprime (Total INV Value)
                total_inventory_value,  # xbase (Total INV Value)
                "Asset",  # xacctype
                session_user,  # zemail (logged user)
                total_inventory_value,  # xamount (Total INV Value - positive)
                Decimal('0.00'),  # xallocation (default 0)
                xsub_values[2]  # xsub (conditional based on zid)
            ])

            # GL Detail Row 4 - Cost of Goods Sold (Credit)
            cursor.execute("""
                INSERT INTO gldetail (
                    ztime, zutime, zid, xvoucher, xrow, xacc, xaccusage, xaccsource,
                    xproj, xcur, xexch, xprime, xbase, xacctype, zemail, xamount, xallocation, xsub
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, [
                current_timestamp,  # ztime
                None,  # zutime
                current_zid,  # zid
                sret_voucher,  # xvoucher (Generated voucher from imtemptrn.xglref)
                4,  # xrow
                row4_account,  # xacc
                xaccusage_values[3],  # xaccusage (conditional based on zid)
                xaccsource_values[3],  # xaccsource (conditional based on zid)
                project_code,  # xproj
                "BDT",  # xcur
                1.0000000000,  # xexch
                -total_inventory_value,  # xprime (Total INV Value minus figured)
                -total_inventory_value,  # xbase (Total INV Value minus figured)
                "Expenditure",  # xacctype
                session_user,  # zemail (logged user)
                total_inventory_value,  # xamount (Total INV Value - positive)
                Decimal('0.00'),  # xallocation (default 0)
                xsub_values[3]  # xsub (conditional based on zid)
            ])

        logger.info(f"Sales return {sre_voucher} processed successfully by {session_user}")

        return JsonResponse({
            'success': True,
            'sre_voucher': sre_voucher,
            'sret_voucher': sret_voucher,
            'message': 'Sales return processed successfully',
            'redirect_url': f'/sales/sales-return-detail/{sre_voucher}/'
        })

    except Exception as e:
        logger.error(f"Error processing sales return: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to process sales return',
            'details': str(e)
        }, status=500)

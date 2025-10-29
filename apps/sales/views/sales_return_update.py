# Standard library imports
import json
import logging
from datetime import datetime
from decimal import Decimal

# Django imports
from django.views.generic import TemplateView
from django.db import transaction, connection
from django.http import JsonResponse, Http404
from django.utils import timezone

# Local application imports
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin
from apps.utils.voucher_generator import generate_voucher_number

# Set up logging
logger = logging.getLogger(__name__)


class SalesReturnUpdateView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    """
    Handle sales return updates - GET shows form, POST processes update
    """
    module_code = 'sales_return_update'
    template_name = 'sales_return_update.html'

    def get_context_data(self, **kwargs):
        """Display the update form with existing data"""
        # Initialize the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Get transaction_id from URL parameters
        transaction_id = kwargs.get('transaction_id')
        current_zid = self.request.session.get('current_zid')

        if not current_zid:
            raise Http404("No business context found")

        if not transaction_id:
            raise Http404("Transaction ID is required")

        # Fetch transaction data
        transaction_data = self.get_transaction_data(current_zid, transaction_id)

        if not transaction_data:
            raise Http404("Transaction not found")

        context.update({
            'transaction_id': transaction_id,
            'header': transaction_data.get('header', {}),
            'items': transaction_data.get('items', []),
            'cart_items_json': json.dumps(transaction_data.get('items', []))
        })

        return context

    def get_transaction_data(self, zid, transaction_id):
        """
        Fetch complete transaction data from imtemptrn and imtemptdt tables
        """
        try:
            with connection.cursor() as cursor:
                # Get transaction header
                cursor.execute("""
                    SELECT ximtmptrn, xdate, xref, xsup, xwh, xproj, xrem
                    FROM imtemptrn
                    WHERE ximtmptrn = %s AND zid = %s
                """, [transaction_id, zid])

                transaction_data = cursor.fetchone()
                if not transaction_data:
                    logger.warning(f"Transaction {transaction_id} not found for ZID {zid}")
                    return None

                # Get cart items with item descriptions from caitem
                cursor.execute("""
                    SELECT d.xitem, c.xdesc, d.xqtyord, d.xunit, d.xrate, d.xval, d.xlineamt, c.xgitem, c.xcitem
                    FROM imtemptdt d
                    LEFT JOIN caitem c ON d.xitem = c.xitem AND d.zid = c.zid
                    WHERE d.ximtmptrn = %s AND d.zid = %s
                    ORDER BY d.xtorlno
                """, [transaction_id, zid])

                cart_items = []
                for item_data in cursor.fetchall():
                    cart_items.append({
                        'item_code': item_data[0],
                        'item_name': item_data[1] or '',  # xdesc from caitem
                        'quantity': float(item_data[2]) if item_data[2] else 0,
                        'unit': item_data[3] or '',
                        'rate': float(item_data[4]) if item_data[4] else 0,
                        'inv_value': float(item_data[5]) if item_data[5] else 0,  # xval
                        'mkt_value': float(item_data[6]) if item_data[6] else 0,  # xlineamt
                        'item_group': item_data[7] or '',  # xgitem from caitem
                        'item_category': item_data[8] or ''  # xcitem from caitem
                    })

                # Extract header data
                header_data = {
                    'ximtmptrn': transaction_data[0],
                    'xdate': transaction_data[1],
                    'xref': transaction_data[2],
                    'xsup': transaction_data[3],
                    'xwh': transaction_data[4],
                    'xproj': transaction_data[5],
                    'xrem': transaction_data[6],
                }

                return {
                    'header': header_data,
                    'items': cart_items
                }

        except Exception as e:
            logger.error(f"Error fetching transaction data: {str(e)}")
            return None

    def post(self, request, **kwargs):
        """
        Handle AJAX POST requests for sales return updates
        """
        transaction_id = kwargs.get('transaction_id')
        return self.process_sales_return_update(request, transaction_id)

    @transaction.atomic
    def process_sales_return_update(self, request, transaction_id):
        """
        Process the sales return update (extracted from original POST logic)
        """
        try:
            data = json.loads(request.body)
            logger.info(f"Received sales return update data for {transaction_id}: {data}")

            # Get current ZID from session
            current_zid = request.session.get('current_zid')
            if not current_zid:
                return JsonResponse({
                    'success': False,
                    'error': 'No business context found'
                }, status=400)

            # Extract form data - handle the actual data structure sent by frontend
            # Frontend sends flat structure, not nested under formData/cartItems
            form_data = {
                'transaction_id': data.get('transaction_id'),
                'transaction_date': data.get('transaction_date'),
                'customer': data.get('customer'),
                'supplier': data.get('supplier'),
                'warehouse': data.get('warehouse'),
                'project': data.get('project'),
                'notes': data.get('notes')
            }
            cart_items = data.get('items', [])

            if not cart_items:
                return JsonResponse({
                    'success': False,
                    'error': 'No items in cart'
                }, status=400)

            # Basic validation - only check for cart items
            # For updates, we allow partial field updates

            with connection.cursor() as cursor:
                # Step 1: Get xglref from imtemptrn
                cursor.execute("""
                    SELECT xglref FROM imtemptrn
                    WHERE zid = %s AND ximtmptrn = %s
                """, [current_zid, transaction_id])

                result = cursor.fetchone()
                if not result:
                    return JsonResponse({
                        'success': False,
                        'error': f'Transaction {transaction_id} not found'
                    }, status=404)

                xglref = result[0]
                logger.info(f"Found xglref: {xglref} for transaction: {transaction_id}")

                # Step 2: Delete existing records in proper order
                if xglref:
                    # Delete from gldetail first (child table)
                    cursor.execute("""
                        DELETE FROM gldetail
                        WHERE xvoucher = %s AND zid = %s
                    """, [xglref, current_zid])
                    logger.info(f"Deleted gldetail records for voucher: {xglref}")

                    # Delete from glheader (parent table)
                    cursor.execute("""
                        DELETE FROM glheader
                        WHERE xvoucher = %s AND zid = %s
                    """, [xglref, current_zid])
                    logger.info(f"Deleted glheader record for voucher: {xglref}")

                # Delete from imtrn
                cursor.execute("""
                    DELETE FROM imtrn
                    WHERE xdocnum = %s AND zid = %s
                """, [transaction_id, current_zid])
                logger.info(f"Deleted imtrn records for transaction: {transaction_id}")

                # Delete from imtemptdt
                cursor.execute("""
                    DELETE FROM imtemptdt
                    WHERE ximtmptrn = %s AND zid = %s
                """, [transaction_id, current_zid])
                logger.info(f"Deleted imtemptdt records for transaction: {transaction_id}")

                # Step 3: Update imtemptrn with new form data (preserve xglref)
                current_timestamp = timezone.now()
                session_user = request.user.username

                # Build dynamic UPDATE query for provided fields only
                update_fields = []
                update_values = []

                # Always update timestamp and user
                update_fields.append("ztime = %s")
                update_values.append(current_timestamp)
                update_fields.append("zutime = %s")
                update_values.append(current_timestamp)
                update_fields.append("zemail = %s")
                update_values.append(session_user)

                # Update fields if provided
                if form_data.get('notes'):
                    update_fields.append("xref = %s")
                    update_values.append(form_data['notes'])

                if form_data.get('transaction_date'):
                    transaction_date = form_data['transaction_date']
                    date_obj = datetime.strptime(transaction_date, '%Y-%m-%d')
                    year = date_obj.year
                    month = f"{date_obj.month:02d}"

                    update_fields.append("xdate = %s")
                    update_values.append(transaction_date)
                    update_fields.append("xyear = %s")
                    update_values.append(year)
                    update_fields.append("xper = %s")
                    update_values.append(month)

                if form_data.get('project'):
                    update_fields.append("xproj = %s")
                    update_values.append(form_data['project'])

                if form_data.get('warehouse'):
                    update_fields.append("xwh = %s")
                    update_values.append(form_data['warehouse'])

                if form_data.get('supplier'):
                    update_fields.append("xsup = %s")
                    update_values.append(form_data['supplier'])

                # Add WHERE clause values
                update_values.extend([current_zid, transaction_id])

                # Execute dynamic UPDATE
                update_sql = f"""
                    UPDATE imtemptrn SET
                        {', '.join(update_fields)}
                    WHERE zid = %s AND ximtmptrn = %s
                """

                cursor.execute(update_sql, update_values)
                logger.info(f"Updated imtemptrn record for transaction: {transaction_id}")

                # Get totals from frontend (already calculated)
                totals = data.get('totals', {})
                total_market_value = Decimal(str(totals.get('totalMktValue', 0)))
                total_inventory_value = Decimal(str(totals.get('totalInvValue', 0)))

                # Step 4: Re-insert cart items into imtemptdt and imtrn
                for idx, item in enumerate(cart_items, 1):
                    # Use 'rate' field from frontend (matches sales_return_confirm.py logic)
                    inv_value = Decimal(str(item.get('rate', 0)))
                    quantity = Decimal(str(item.get('quantity', 0)))
                    item_total = quantity * inv_value
                    mkt_value = Decimal(str(item.get('amount', item_total)))

                    # Generate individual voucher for each item in imtemptdt
                    item_voucher = generate_voucher_number(current_zid, 'SRE', 'imtrn', 'ximtrnnum')
                    
                    # Insert into imtemptdt with correct column structure
                    cursor.execute("""
                        INSERT INTO imtemptdt (
                            ztime, zutime, zid, ximtmptrn, xtorlno, xitem, xqtyord, xunit, 
                            ximtrnnum, xrate, xval, zemail, xqtyreq, xdatesch, xfrslnum, 
                            xtoslnum, xlineamt
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, [
                        current_timestamp,  # ztime
                        current_timestamp,  # zutime
                        current_zid,  # zid
                        transaction_id,  # ximtmptrn
                        idx,  # xtorlno - item serial number
                        item.get('item_code', ''),  # xitem
                        quantity,  # xqtyord
                        'Pcs',  # xunit - default unit
                        item_voucher,  # ximtrnnum - individual SRE voucher
                        inv_value,  # xrate - INV Value (using 'rate' from frontend)
                        item_total,  # xval - INV Value total (quantity * rate)
                        request.user.email,  # zemail - logged user
                        quantity,  # xqtyreq - same as xqtyord
                        '2999-12-31',  # xdatesch - default date
                        0,  # xfrslnum - default 0
                        0,  # xtoslnum - default 0
                        mkt_value  # xlineamt - MKT Value (using 'amount' from frontend)
                    ])

                    # Insert into imtrn
                    # Use the same calculation as above

                    # Use form data or get existing values from database
                    item_warehouse = form_data.get('warehouse', '')
                    item_project = form_data.get('project', '')
                    item_date = form_data.get('transaction_date', current_timestamp.strftime('%Y-%m-%d'))

                    # Parse date for imtrn
                    item_date_obj = datetime.strptime(item_date, '%Y-%m-%d')
                    item_year = item_date_obj.year
                    item_month = f"{item_date_obj.month:02d}"

                    cursor.execute("""
                        INSERT INTO imtrn (
                            ztime, zutime, zid, ximtrnnum, xitem, xwh, xdate, xyear, xper, xqty, xval,
                            xvalpost, xdoctype, xdocnum, xdocrow, xaltqty, xproj, xdateexp,
                            xdaterec, xaction, xsign, xmember
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, [
                        current_timestamp,  # ztime
                        current_timestamp,  # zutime (update timestamp)
                        current_zid,  # zid
                        item_voucher,  # ximtrnnum (individual item voucher)
                        item.get('item_code', ''),  # xitem - frontend sends item_code
                        item_warehouse,  # xwh
                        item_date,  # xdate
                        item_year,  # xyear
                        item_month,  # xper
                        quantity,  # xqty
                        item_total,  # xval (quantity * inv_value)
                        item_total,  # xvalpost (same as xval)
                        'SRE-',  # xdoctype
                        transaction_id,  # xdocnum
                        str(idx),  # xdocrow (row number as string)
                        0,  # xaltqty (default 0)
                        item_project,  # xproj
                        item_date,  # xdateexp
                        item_date,  # xdaterec
                        'Return',  # xaction
                        1,  # xsign (default 1)
                        session_user  # xmember
                    ])

                # Step 5: Re-insert GL entries if xglref exists
                if xglref:
                    # Get date for GL entries (use provided date or current date)
                    gl_date = form_data.get('transaction_date', current_timestamp.strftime('%Y-%m-%d'))
                    gl_date_obj = datetime.strptime(gl_date, '%Y-%m-%d')
                    gl_year = gl_date_obj.year
                    gl_month = f"{gl_date_obj.month:02d}"

                    # Insert into glheader
                    cursor.execute("""
                        INSERT INTO glheader (
                            ztime, zutime, zid, xvoucher, xref, xdate, xlong, xpostflag,
                            xyear, xper, xstatusjv, xdatedue, zemail, xnumofper, xnote,
                            xmember, xapproved, xaction
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, [
                        current_timestamp,  # ztime
                        current_timestamp,  # zutime (update timestamp)
                        current_zid,  # zid
                        xglref,  # xvoucher (existing voucher)
                        xglref,  # xref
                        gl_date,  # xdate
                        f"** Sales Return Updated By System On {gl_date} **",  # xlong
                        True,  # xpostflag
                        gl_year,  # xyear
                        gl_month,  # xper
                        "Balanced",  # xstatusjv
                        gl_date,  # xdatedue
                        session_user,  # zemail
                        0,  # xnumofper
                        f"***System Updated Sales Return voucher From IM- {gl_date}",  # xnote
                        session_user,  # xmember
                        1,  # xapproved
                        "Journal"  # xaction
                    ])

                    # Insert into gldetail (following same pattern as confirm)
                    project_code = form_data.get('project', '')

                    # Account logic based on session ZID (same as sales_return_confirm.py)
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
                        current_timestamp, None, current_zid, xglref, 1, row1_account,
                        xaccusage_values[0], xaccsource_values[0], project_code, "BDT", 1.0000000000,
                        total_market_value, total_market_value, "Income", session_user,
                        total_market_value, Decimal('0.00'), xsub_values[0]
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
                        current_timestamp, None, current_zid, xglref, 2, row2_account,
                        xaccusage_values[1], xaccsource_values[1], project_code, "BDT", 1.0000000000,
                        -total_market_value, -total_market_value, "Asset", session_user,
                        total_market_value, Decimal('0.00'), xsub_values[1]
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
                        current_timestamp, None, current_zid, xglref, 3, row3_account,
                        xaccusage_values[2], xaccsource_values[2], project_code, "BDT", 1.0000000000,
                        total_inventory_value, total_inventory_value, "Asset", session_user,
                        total_inventory_value, Decimal('0.00'), xsub_values[2]
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
                        current_timestamp, None, current_zid, xglref, 4, row4_account,
                        xaccusage_values[3], xaccsource_values[3], project_code, "BDT", 1.0000000000,
                        -total_inventory_value, -total_inventory_value, "Expenditure", session_user,
                        total_inventory_value, Decimal('0.00'), xsub_values[3]
                    ])

            logger.info(f"Sales return {transaction_id} updated successfully by {session_user}")

            return JsonResponse({
                'success': True,
                'transaction_id': transaction_id,
                'xglref': xglref,
                'message': 'Sales return updated successfully',
                'redirect_url': f'/sales/sales-return-detail/{transaction_id}/'
            })

        except Exception as e:
            logger.error(f"Error updating sales return {transaction_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to update sales return',
                'details': str(e)
            }, status=500)

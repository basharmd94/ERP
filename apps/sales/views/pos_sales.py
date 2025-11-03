# Standard library imports
import json
import logging
from datetime import datetime

# Django imports
from django.db import transaction, connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from apps.utils.average_price_calculation import get_average_prices_bulk
from apps.utils.items_check_inventory import items_check_inventory
from apps.utils.voucher_generator import generate_voucher_number

# Set up logging
logger = logging.getLogger(__name__)





@csrf_exempt
@transaction.atomic
@login_required
def pos_complete_sale(request):
    """
    AJAX endpoint to complete a POS sale with inventory validation
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        logger.info(f"Received sale data: {data}")

        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({
                'success': False,
                'error': 'No business context found'
            }, status=400)

        # Extract items from the request data
        items = data.get('items', [])
        if not items:
            return JsonResponse({
                'success': False,
                'error': 'No items found in the order'
            }, status=400)

        # Validate inventory for all items
        inventory_validation = items_check_inventory(items, current_zid)

        if not inventory_validation['success']:
            # Return validation errors with detailed information
            return JsonResponse({
                'success': False,
                'message': inventory_validation['message'],
                'errors': inventory_validation['errors'],
                'validation_failed': True
            }, status=400)

        # If validation passes, extract additional data
        bank_name = data.get('bank_name', '')
        payment_method = data.get('payment_method', 'Cash Sale')
        card_number = data.get('card_number', '')
        card_amount = data.get('card_amount', 0)
        cash_amount = data.get('cash_amount', 0)

        # Extract totals and VAT information
        totals = data.get('totals', {})
        subtotal = totals.get('subtotal', 0)
        tax_amount = totals.get('tax_amount', 0)
        grand_total = totals.get('grand_total', 0)

        # Log individual item VAT amounts, selling units, and unit costs
        total_individual_vat = 0
        for item in items:
            item_vat = float(item.get('item_vat', 0))
            selling_unit = item.get('xunitstk', 'N/A')
            unit_cost = float(item.get('item_cost', 0))
            total_individual_vat += item_vat
            logger.info(f"Item {item.get('xitem')}: VAT = {item_vat}, Selling Unit = {selling_unit}, Unit Cost = {unit_cost}")

        logger.info(f"Inventory validation successful for order with {len(items)} items")

        # Process the sale with database insertions
        try:
            with transaction.atomic():
                # Generate order number
                order_number = generate_voucher_number(current_zid, 'CO--', 'opord', 'xordernum')

                # Extract additional data
                discounts = data.get('discounts', {})
                header_info = data.get('header_info', {})
                timestamp_str = data.get('timestamp', datetime.now().isoformat())

                # Parse timestamp
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.now()

                current_date = timestamp.strftime('%Y-%m-%d')
                current_year = timestamp.year
                current_month = timestamp.month

                # Get session user
                session_user = request.session.get('username', 'counter@fixit.com')

                # Map payment method
                payment_type_map = {
                    'cash': 'Cash Sale',
                    'card': 'Card Sale',
                    'credit': 'Credit Sale'
                }
                xsltype = payment_type_map.get(payment_method, 'Cash Sale')

                # Use single cursor for all database operations
                with connection.cursor() as cursor:
                    opord_sql = """
                        INSERT INTO opord (
                            ztime, zutime, zid, xordernum, xdate, xcus, xstatusord, xcur,
                            xdisc, xdiscf, xwh, zemail, xemail, xdtwotax, xdtdisc, xdttax,
                            xval, xdiscamt, xtotamt, xsp, xsltype, xsalescat, xtrnord,
                            xdocnum, xdtcomm, xcounterno, xyear, xper, xemp, xmobile,
                            xdatecon, xamtpaid, xamt
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s
                        )
                    """

                    cursor.execute(opord_sql, [
                        timestamp,  # ztime
                        timestamp,  # zutime
                        current_zid,  # zid
                        order_number,  # xordernum
                        current_date,  # xdate
                        header_info.get('customer_name', 'CUS-000001'),  # xcus
                        'Confirmed',  # xstatusord
                        'BDT',  # xcur
                        discounts.get('percent_discount', 0),  # xdisc
                        discounts.get('fixed_discount', 0),  # xdiscf
                        header_info.get('warehouse', 'Fixit Gulshan'),  # xwh
                        session_user,  # zemail
                        session_user,  # xemail
                        0.00,  # xdtwotax
                        discounts.get('percent_discount_amount', 0),  # xdtdisc
                        tax_amount,  # xdttax
                        0.00,  # xval
                        discounts.get('total_discount_amount', 0),  # xdiscamt
                        grand_total,  # xtotamt
                        header_info.get('salesman', 'Ohidul'),  # xsp
                        xsltype,  # xsltype
                        bank_name,  # xsalescat
                        'CO--',  # xtrnord
                        card_number or 0,  # xdocnum
                        card_amount,  # xdtcomm
                        'CT04',  # xcounterno
                        current_year,  # xyear
                        current_month,  # xper
                        session_user,  # xemp
                        header_info.get('customer_phone', ''),  # xmobile
                        timestamp,  # xdatecon
                        0.00,  # xamtpaid
                        7.50  # xamt
                    ])

                    # Get average prices for all items
                    item_codes = [item['xitem'] for item in items]
                    average_prices = get_average_prices_bulk(current_zid, item_codes, current_date)

                    # Insert into opodt and imtrn tables for each item
                    for idx, item in enumerate(items, 1):
                        # Generate IS-- number for this item
                        is_number = generate_voucher_number(current_zid, 'IS--', 'imtrn', 'ximtrnnum')

                        # Insert into opodt table
                        opodt_sql = """
                        INSERT INTO opodt (
                            ztime, zid, xordernum, xrow, xcode, xitem, xstype, xwh,
                            xqtyreq, xqtyord, xunitsel, xcur, xrate, xlineamt, xdtwotax,
                            xdttax, ximtrnnum, xcost, xsign, xdesc
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s
                        )
                        """

                        cursor.execute(opodt_sql, [
                            timestamp,  # ztime
                            current_zid,  # zid
                            order_number,  # xordernum
                            str(idx),  # xrow
                            item['xitem'],  # xcode
                            item['xitem'],  # xitem
                            'Stock-N-Sell',  # xstype
                            header_info.get('warehouse', 'Fixit Gulshan'),  # xwh
                            f"{float(item['quantity']):.3f}",  # xqtyreq
                            f"{float(item['quantity']):.3f}",  # xqtyord
                            item.get('xunitstk', 'Pcs'),  # xunitsel
                            'BDT',  # xcur
                            f"{float(item['xstdprice']):.4f}",  # xrate
                            f"{float(item['total']):.2f}",  # xlineamt
                            f"{float(item['total']):.2f}",  # xdtwotax
                            f"{float(item.get('item_vat', 0)):.2f}",  # xdttax
                            is_number,  # ximtrnnum
                            f"{float(item.get('item_cost', 0)):.2f}",  # xcost
                            0,  # xsign
                            item['xdesc']  # xdesc
                        ])

                        # Calculate xval for imtrn using average price
                        avg_price = average_prices.get(item['xitem'], 0)
                        xval = float(avg_price) * float(item['quantity'])

                        # Insert into imtrn table
                        imtrn_sql = """
                            INSERT INTO imtrn (
                                ztime, zid, ximtrnnum, xitem, xitemrow, xwh, xdate, xyear,
                                xper, xqty, xval, xvalpost, xdoctype, xdocnum, xdocrow,
                                xdateexp, xdaterec, xlicense, xcus, xaction, xsign, xtime,
                                zemail, xtrnim, xstdprice
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s
                            )
                        """

                        cursor.execute(imtrn_sql, [
                            timestamp,  # ztime
                            current_zid,  # zid
                            is_number,  # ximtrnnum
                            item['xitem'],  # xitem
                            xsltype,  # xitemrow (payment_method)
                            header_info.get('warehouse', 'Fixit Gulshan'),  # xwh
                            current_date,  # xdate
                            str(current_year),  # xyear
                            str(current_month),  # xper
                            f"{float(item['quantity']):.3f}",  # xqty
                            f"{float(xval):.6f}",  # xval
                            "0.000000",  # xvalpost
                            'IS--',  # xdoctype
                            order_number,  # xdocnum
                            idx,  # xdocrow
                            current_date,  # xdateexp
                            current_date,  # xdaterec
                            '',  # xlicense
                            header_info.get('customer_name', 'CUS-000001'),  # xcus
                            'Issue',  # xaction
                            '-1',  # xsign
                            timestamp,  # xtime
                            session_user,  # zemail
                            'IS--',  # xtrnim
                            f"{float(item['xstdprice']):.4f}"  # xstdprice
                        ])

                logger.info(f"Sale processed successfully. Order Number: {order_number}")

                return JsonResponse({
                    'success': True,
                    'order_number': order_number,
                    'message': 'Sale processed successfully',
                    'validation_passed': True
                })

        except Exception as e:
            logger.error(f"Error processing sale: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Failed to process sale: {str(e)}'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Sale processing error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

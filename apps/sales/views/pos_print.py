from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.db import connection
import logging

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def pos_print_slip(request, transaction_id):
    """
    View to generate and display POS slip for printing
    Retrieves transaction data from opord and opodt tables
    """
    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            logger.warning(f"No business context found for user: {request.user.username}")
            raise Http404("No business context found")

        # Get transaction data using raw SQL with comprehensive JOIN
        with connection.cursor() as cursor:
            # Use the improved SQL query with proper JOINs
            comprehensive_sql = """
            SELECT
                o.xordernum,
                o.xdate,
                o.xcus, -- customer code
                o.xwh, -- warehouse
                o.zemail,
                o.xdtdisc,
                o.xdttax AS header_tax,
                o.xtotamt, -- total amount
                o.xsp, -- salesman
                o.xsltype,
                o.xsalescat, -- bank name
                o.xdocnum, -- card number
                o.xdtcomm, -- card amount
                o.xmobile, -- mobile
                d.xrow,  -- sl number
                d.xitem,
                i.xdesc AS xitemname,   -- item name from caitem
                d.xqtyreq,  -- quantity
                d.xunitsel, -- unit
                d.xrate, -- rate
                d.xlineamt, -- lineamount
                d.xdttax AS detail_tax,
                -- Additional customer info from cacus
                c.xorg as customer_name,
                c.xadd1 as customer_address1,
                c.xadd2 as customer_address2,
                c.xcity as customer_city,
                c.xstate as customer_state,
                c.xzip as customer_zip,
                c.xphone as customer_phone,
                -- Additional item info
                i.xbarcode,
                i.xstdprice
            FROM opord AS o
            INNER JOIN opodt AS d
                ON o.zid = d.zid
                AND o.xordernum = d.xordernum
            LEFT JOIN caitem AS i
                ON d.zid = i.zid
                AND d.xitem = i.xitem
            LEFT JOIN cacus AS c
                ON o.zid = c.zid
                AND o.xcus = c.xcus
            WHERE
                o.zid = %s
                AND o.xordernum = %s
            ORDER BY d.xrow
            """

            cursor.execute(comprehensive_sql, [current_zid, transaction_id])
            rows = cursor.fetchall()

            if not rows:
                logger.warning(f"Transaction {transaction_id} not found for ZID {current_zid}")
                raise Http404("Transaction not found")

            # Convert to list of dictionaries
            columns = [desc[0] for desc in cursor.description]
            all_data = [dict(zip(columns, row)) for row in rows]

            # Extract header data from first row (same for all rows)
            first_row = all_data[0]
            header_data = {
                'xordernum': first_row['xordernum'],
                'xdate': first_row['xdate'],
                'xcus': first_row['xcus'],
                'xwh': first_row['xwh'],
                'zemail': first_row['zemail'],
                'xdtdisc': first_row['xdtdisc'],
                'header_tax': first_row['header_tax'],
                'xtotamt': first_row['xtotamt'],
                'xsp': first_row['xsp'],
                'xsltype': first_row['xsltype'],
                'xsalescat': first_row['xsalescat'],
                'xdocnum': first_row['xdocnum'],
                'xdtcomm': first_row['xdtcomm'],
                'xmobile': first_row['xmobile'],
                'customer_name': first_row['customer_name'],
                'customer_address1': first_row['customer_address1'],
                'customer_address2': first_row['customer_address2'],
                'customer_city': first_row['customer_city'],
                'customer_state': first_row['customer_state'],
                'customer_zip': first_row['customer_zip'],
                'customer_phone': first_row['customer_phone'],
            }

            # Extract detail data (unique for each row)
            detail_data = []
            for row in all_data:
                detail_data.append({
                    'xrow': row['xrow'],
                    'xitem': row['xitem'],
                    'xdesc': row['xitemname'],  # Using the proper item name from caitem
                    'xqtyord': row['xqtyreq'],  # Using the correct quantity field
                    'xunit': row['xunitsel'],   # Using the correct unit field
                    'xrate': row['xrate'],
                    'line_total': row['xlineamt'],  # Using the correct line amount field
                    'detail_tax': row['detail_tax'],
                    'xbarcode': row['xbarcode'],
                    'xstdprice': row['xstdprice'],
                })

        # Calculate totals using the new field names
        subtotal = sum(float(item['line_total'] or 0) for item in detail_data)
        discount_amount = float(header_data['xdtdisc'] or 0)
        tax_amount = float(header_data['header_tax'] or 0)
        grand_total = float(header_data['xtotamt'] or 0)  # Use the total amount from header

        # If grand total is not available, calculate it
        if grand_total == 0:
            grand_total = subtotal - discount_amount + tax_amount

        # Get business information
        business_sql = """
        SELECT name, zid
        FROM authentication_business
        WHERE zid = %s
        """

        with connection.cursor() as cursor:
            cursor.execute(business_sql, [current_zid])
            business_row = cursor.fetchone()
            business_data = {
                'name': business_row[0] if business_row else 'Unknown Business',
                'zid': business_row[1] if business_row else current_zid
            }

        # Prepare context for template
        context = {
            'transaction_id': transaction_id,
            'header': header_data,
            'details': detail_data,
            'business': business_data,
            'totals': {
                'subtotal': subtotal,
                'discount': discount_amount,
                'tax': tax_amount,
                'grand_total': grand_total
            },
            'current_zid': current_zid,
        }

        return render(request, 'pos_print.html', context)

    except Exception as e:
        logger.error(f"Error generating POS slip for transaction {transaction_id}: {str(e)}")
        raise Http404(f"Error generating slip: {str(e)}")

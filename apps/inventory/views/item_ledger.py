from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin



import logging

# Get logger for this module
logger = logging.getLogger(__name__)

class ItemLedgerView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'inventory_reports_item_ledger'
    template_name = 'item_ledger.html'
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


def get_item_ledger(request):
    # get data from imtrn model with comprehensive ledger calculation
    try:
        # Get filter parameters from request
        warehouse = request.GET.get('warehouse', '').strip()
        from_date = request.GET.get('from_date', '').strip()
        to_date = request.GET.get('to_date', '').strip()
        select_item = request.GET.get('select_item', '').strip()

        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            logger.warning(f"No business context found for user: {request.user.username}")
            return JsonResponse({'error': 'No business context found'}, status=400)

        # Validate required parameters
        if not select_item:
            return JsonResponse({
                'success': True,
                'data': [],
                'count': 0,
                'message': 'Please select an item to view ledger details'
            })

        if not from_date:
            return JsonResponse({
                'success': False,
                'error': 'From date is required'
            }, status=400)

        # Build the comprehensive SQL query using the user's improved structure
        from django.db import connection

        sql_query = """
        WITH prior_balance AS (
            SELECT
                COALESCE(SUM(xqty * xsign), 0) AS opening_qty,
                COALESCE(SUM(xval * xsign), 0) AS opening_val
            FROM imtrn
            WHERE zid = %s
              AND xitem = %s
              AND xdate < %s
        """

        # Add warehouse filter to prior_balance if specified
        params = [current_zid, select_item, from_date]
        if warehouse:
            sql_query += " AND xwh = %s"
            params.append(warehouse)

        sql_query += """
        ),
        filtered_transactions AS (
            SELECT
                xdate,
                xdocnum,
                ximtrnnum,
                xitem,
                xsign,
                xqty,
                SUM(xqty * xsign) AS txn_qty,
                SUM(xval * xsign) AS txn_val
            FROM imtrn
            WHERE zid = %s
              AND xitem = %s
              AND xdate >= %s
        """

        # Add parameters for filtered_transactions
        params.extend([current_zid, select_item, from_date])

        # Add optional to_date filter
        if to_date:
            sql_query += " AND xdate <= %s"
            params.append(to_date)

        # Add optional warehouse filter
        if warehouse:
            sql_query += " AND xwh = %s"
            params.append(warehouse)

        sql_query += """
            GROUP BY xdate, xdocnum, ximtrnnum, xitem, xsign, xqty, xval
        ),
        running AS (
            SELECT
                ft.*,
                pb.opening_qty,
                pb.opening_val,
                SUM(ft.txn_qty) OVER (
                    ORDER BY ft.xdate, ft.xdocnum, ft.ximtrnnum
                    ROWS UNBOUNDED PRECEDING
                ) AS cum_qty,
                SUM(ft.txn_val) OVER (
                    ORDER BY ft.xdate, ft.xdocnum, ft.ximtrnnum
                    ROWS UNBOUNDED PRECEDING
                ) AS cum_val
            FROM filtered_transactions ft
            CROSS JOIN prior_balance pb
        )

        SELECT
            xdate,
            xdocnum,
            ximtrnnum,
            xitem,
            CASE
                WHEN xsign = 1 THEN 'Receipt'
                WHEN xsign = -1 THEN 'Issue'
                ELSE 'Unknown'
            END AS transaction_type,
            xqty AS transaction_qty,
            ROUND(ABS(txn_val) / NULLIF(xqty, 0), 2) AS transaction_rate,
            ROUND(txn_val, 2) AS transaction_value,
            -- Balance columns
            ROUND(opening_qty + cum_qty, 3) AS balance_qty,
            ROUND(
                (opening_val + cum_val) / NULLIF(opening_qty + cum_qty, 0),
                2
            ) AS balance_rate,
            ROUND(opening_val + cum_val, 2) AS balance_value,
            -- Opening reference
            ROUND(opening_qty, 3) AS opening_qty,
            ROUND(opening_val, 2) AS opening_val
        FROM running
        ORDER BY xdate, xdocnum, ximtrnnum
        """

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()

            # Convert to list of dictionaries
            data = []
            for row in results:
                row_dict = dict(zip(columns, row))
                # Convert date to string for JSON serialization
                if row_dict.get('xdate'):
                    row_dict['xdate'] = row_dict['xdate'].strftime('%Y-%m-%d')
                data.append(row_dict)

        # Log filter parameters for debugging
        logger.info(f"Item ledger query executed - ZID: {current_zid}, "
                   f"Item: {select_item}, From Date: {from_date}, "
                   f"To Date: {to_date}, Warehouse: {warehouse}, "
                   f"Records found: {len(data)}")

        return JsonResponse({
            'success': True,
            'data': data,
            'count': len(data),
            'filters_applied': {
                'zid': current_zid,
                'warehouse': warehouse,
                'from_date': from_date,
                'to_date': to_date,
                'select_item': select_item
            }
        })

    except Exception as e:
        logger.error(f"Error fetching item ledger data: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to fetch item ledger data: {str(e)}'
        }, status=500)

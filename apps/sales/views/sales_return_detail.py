from django.views.generic import TemplateView
from django.db import connection
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin, ModulePermissionMixin
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CLASS-BASED VIEWS FOR URL PARAMETER HANDLING
# ============================================================================

class SalesReturnDetailView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    """
    Django class-based view for sales return detail template rendering
    """
    template_name = 'sales_return_detail.html'
    module_code = 'sales_return_detail'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Get transaction ID from URL parameter
        transaction_id = kwargs.get('transaction_id')
        if transaction_id:
            context['transaction_id'] = transaction_id

            # Get sales return data for the template
            sales_return_data = self.get_sales_return_data(transaction_id)
            context.update(sales_return_data)

        return context

    def get_sales_return_data(self, ximtmptrn):
        """
        Retrieve sales return data for template context
        """
        try:
            current_zid = self.request.session.get('current_zid')
            if not current_zid:
                return {'error': 'No business context found'}

            # Use the same SQL query as the AJAX endpoint
            query = """
                SELECT
                    t.ximtmptrn,
                    t.xdate,
                    t.xrem,
                    t.xproj,
                    t.xwh,
                    t.zemail,
                    t.xglref,
                    t.xstatustrn,
                    d.xtorlno,
                    d.xitem,
                    d.xqtyord,
                    d.xunit,
                    d.ximtrnnum,
                    d.xrate,
                    d.xval,
                    d.xlineamt
                FROM imtemptrn t
                INNER JOIN imtemptdt d
                    ON t.ximtmptrn = d.ximtmptrn
                    AND t.zid = d.zid
                WHERE t.zid = %s
                  AND t.ximtmptrn = %s
            """

            with connection.cursor() as cursor:
                cursor.execute(query, [current_zid, ximtmptrn])
                rows = cursor.fetchall()

                if not rows:
                    return {
                        'error': 'No data found for the specified sales return transaction',
                        'header': None,
                        'line_items': [],
                        'totals': {}
                    }

                # Process the data
                header_data = None
                line_items = []

                for row in rows:
                    # Header data (same for all rows)
                    if header_data is None:
                        header_data = {
                            'ximtmptrn': row[0],
                            'xdate': row[1].strftime('%Y-%m-%d') if row[1] else '',
                            'xrem': row[2] or '',
                            'xproj': row[3] or '',
                            'xwh': row[4] or '',
                            'zemail': row[5] or '',
                            'xglref': row[6] or '',
                            'xstatustrn': row[7] or ''
                        }

                    # Line item data
                    line_item = {
                        'xtorlno': row[8] or '',
                        'xitem': row[9] or '',
                        'xqtyord': float(row[10]) if row[10] else 0.0,
                        'xunit': row[11] or '',
                        'ximtrnnum': row[12] or '',
                        'xrate': float(row[13]) if row[13] else 0.0,
                        'xval': float(row[14]) if row[14] else 0.0,
                        'xlineamt': float(row[15]) if row[15] else 0.0
                    }
                    line_items.append(line_item)

                # Calculate totals
                total_quantity = sum(item['xqtyord'] for item in line_items)
                total_value = sum(item['xval'] for item in line_items)
                total_line_amount = sum(item['xlineamt'] for item in line_items)

                return {
                    'header': header_data,
                    'line_items': line_items,
                    'totals': {
                        'total_quantity': total_quantity,
                        'total_value': total_value,
                        'total_line_amount': total_line_amount,
                        'item_count': len(line_items)
                    }
                }

        except Exception as e:
            logger.error(f"Error retrieving sales return data for template: {str(e)}")
            return {
                'error': 'An error occurred while retrieving sales return details',
                'header': None,
                'line_items': [],
                'totals': {}
            }

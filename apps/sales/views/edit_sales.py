from django.views.generic import TemplateView
from django.http import Http404
from django.db import connection
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin
import logging

# Set up logging
logger = logging.getLogger(__name__)



class SalesEditView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'edit_sales'
    template_name = 'edit_sales.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
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
            'transaction_data': transaction_data,
            'transaction_id': transaction_id
        })

        return context
    
    def get_transaction_data(self, zid, transaction_id):
        """
        Fetch complete transaction data from opord and opodt tables
        """
        try:
            with connection.cursor() as cursor:
                # Comprehensive query to get header and item details
                comprehensive_sql = """
                    SELECT 
                        o.ztime, o.zid, o.xordernum, o.xdate, o.xcus, o.xstatusord, o.xcur,
                        o.xdisc, o.xdiscf, o.xwh, o.zemail, o.xemail, o.xdtwotax, o.xdtdisc, o.xdttax,
                        o.xval, o.xdiscamt, o.xtotamt, o.xsp, o.xsltype, o.xsalescat, o.xtrnord,
                        o.xdocnum, o.xdtcomm, o.xcounterno, o.xyear, o.xper, o.xemp, o.xmobile,
                        o.xdatecon, o.xamtpaid, o.xamt,
                        
                        -- Item details from opodt
                        d.xrow, d.xcode, d.xitem, d.xstype, d.xqtyreq, d.xqtyord, d.xunitsel,
                        d.xrate, d.xlineamt, d.xdtwotax as item_subtotal, d.xdttax as item_tax, 
                        d.ximtrnnum, d.xcost, d.xsign, d.xdesc,
                        
                        -- Customer details
                        c.xorg as customer_name,
                        c.xadd1 as customer_address1,
                        c.xadd2 as customer_address2,
                        c.xmobile as customer_mobile
                        
                    FROM opord o
                    LEFT JOIN opodt d ON o.zid = d.zid AND o.xordernum = d.xordernum
                    LEFT JOIN cacus c ON o.zid = c.zid AND o.xcus = c.xcus
                    WHERE o.zid = %s AND o.xordernum = %s
                    ORDER BY d.xrow
                """
                
                cursor.execute(comprehensive_sql, [zid, transaction_id])
                rows = cursor.fetchall()
                
                if not rows:
                    logger.warning(f"Transaction {transaction_id} not found for ZID {zid}")
                    return None
                
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
                    'xemail': first_row['xemail'],
                    'xdtdisc': first_row['xdtdisc'],
                    'xdisc': first_row['xdisc'],
                    'xdiscf': first_row['xdiscf'],
                    'xdttax': first_row['xdttax'],
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
                    'customer_mobile': first_row['customer_mobile'],
                    'xstatusord': first_row['xstatusord'],
                    'xcur': first_row['xcur'],
                    'xdiscamt': first_row['xdiscamt']
                }
                
                # Extract item details
                items = []
                for row_data in all_data:
                    if row_data['xitem']:  # Only add rows with items
                        items.append({
                            'xrow': row_data['xrow'],
                            'xcode': row_data['xcode'],
                            'xitem': row_data['xitem'],
                            'xdesc': row_data['xdesc'],
                            'xstype': row_data['xstype'],
                            'xqtyreq': row_data['xqtyreq'],
                            'xqtyord': row_data['xqtyord'],
                            'xunitsel': row_data['xunitsel'],
                            'xrate': row_data['xrate'],
                            'xlineamt': row_data['xlineamt'],
                            'item_subtotal': row_data['item_subtotal'],
                            'item_tax': row_data['item_tax'],
                            'ximtrnnum': row_data['ximtrnnum'],
                            'xcost': row_data['xcost'],
                            'xsign': row_data['xsign']
                        })
                
                return {
                    'header': header_data,
                    'items': items
                }
                
        except Exception as e:
            logger.error(f"Error fetching transaction data: {str(e)}")
            return None

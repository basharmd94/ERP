from django.views.generic import TemplateView
from django.db import connection
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin, ModulePermissionMixin


class POGrnDetailView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    template_name = 'po_grn_detail.html'
    module_code = 'po_grn_detail'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        transaction_id = kwargs.get('transaction_id')
        if transaction_id:
            context['transaction_id'] = transaction_id
            data = self.get_grn_data(transaction_id)
            context.update(data)
        return context

    def get_grn_data(self, xgrnnum):
        zid = self.request.session.get('current_zid')
        if not zid:
            return {'error': 'No business context found', 'header': None, 'line_items': [], 'totals': {}}

        query = """
            SELECT
                grn.xgrnnum,
                grn.xdate,
                grn.xrem,
                grn.xproj,
                grn.xwh,
                grn.zemail,
                grn.xstatusgrn,
                grn.xpornum,
                po.xdate AS po_date,
                grn.xconfirmt,
                grn.xsup,
                s.xorg AS supplier_name,
                grn.xref,
                d.xrow,
                d.xitem,
                i.xdesc,
                d.xqty,
                d.xqtygrn,
                i.xunitstk,
                d.xrate,
                d.xlineamt
            FROM pogrn grn
            LEFT JOIN pogdt d ON d.zid = grn.zid AND d.xgrnnum = grn.xgrnnum
            LEFT JOIN caitem i ON i.zid = d.zid AND i.xitem = d.xitem
            LEFT JOIN poord po ON po.zid = grn.zid AND po.xpornum = grn.xpornum
            LEFT JOIN casup s ON s.zid = grn.zid AND s.xsup = grn.xsup
            WHERE grn.zid = %s AND grn.xgrnnum = %s
            ORDER BY d.xrow
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [zid, xgrnnum])
            rows = cursor.fetchall()

        if not rows:
            return {'error': 'No data found for the specified GRN', 'header': None, 'line_items': [], 'totals': {}}

        header = None
        line_items = []
        for row in rows:
            if header is None:
                header = {
                    'xgrnnum': row[0] or '',
                    'xdate': row[1].strftime('%Y-%m-%d') if row[1] else '',
                    'xrem': row[2] or '',
                    'xproj': row[3] or '',
                    'xwh': row[4] or '',
                    'zemail': row[5] or '',
                    'xstatusgrn': row[6] or '',
                    'xpornum': row[7] or '',
                    'po_date': row[8].strftime('%Y-%m-%d') if row[8] else '',
                    'xconfirmt': row[9].strftime('%Y-%m-%d') if row[9] else '',
                    'xsup': row[10] or '',
                    'supplier_name': row[11] or '',
                    'xref': row[12] or ''
                }

            line_items.append({
                'xrow': int(row[13]) if row[13] else 0,
                'xitem': row[14] or '',
                'xdesc': row[15] or (row[14] or ''),
                'xqty': float(row[16]) if row[16] is not None else 0.0,
                'xqtygrn': float(row[17]) if row[17] is not None else 0.0,
                'xunitstk': row[18] or '',
                'xrate': float(row[19]) if row[19] is not None else 0.0,
                'xlineamt': float(row[20]) if row[20] is not None else 0.0,
            })

        totals = {
            'item_count': len(line_items),
            'total_quantity': sum(item['xqtygrn'] for item in line_items),
            'total_value': sum(item['xlineamt'] for item in line_items),
        }
        next_prev = {'next_grn': None, 'prev_grn': None}

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT MIN(xgrnnum) FROM pogrn WHERE zid = %s AND xgrnnum > %s
                """,
                [zid, xgrnnum]
            )
            r = cursor.fetchone()
            next_prev['next_grn'] = r[0] if r and r[0] else None

            cursor.execute(
                """
                SELECT MAX(xgrnnum) FROM pogrn WHERE zid = %s AND xgrnnum < %s
                """,
                [zid, xgrnnum]
            )
            r = cursor.fetchone()
            next_prev['prev_grn'] = r[0] if r and r[0] else None

        return {'header': header, 'line_items': line_items, 'totals': totals, **next_prev}

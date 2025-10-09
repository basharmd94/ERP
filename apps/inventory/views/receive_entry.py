from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin
from apps.utils.voucher_generator import generate_voucher_number
from django.db import transaction, connection

import logging

logger = logging.getLogger(__name__)

class ReceiveEntryView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'receive_entry'
    template_name = 'receive_entry.html'

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

@login_required
@csrf_protect
@transaction.atomic
@require_http_methods(["POST"])
def save_receive_entry(request):
    if request.method == 'POST':
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({'error': 'No business context found'}, status=400)

        # Get prefix from form input (JavaScript sends 'xprefix')
        prefix = request.POST.get('xprefix')  # Default to 'REC-' if not provided
        # Generate voucher number using the generic function
        voucher_number = generate_voucher_number(
            zid=current_zid,
            prefix=prefix,
            table='imtemptrn',
            column='ximtmptrn'
        )

        # Use raw SQL to insert record (Django ORM has issues with composite primary keys on legacy tables)
        try:
            with connection.cursor() as cursor:
                insert_sql = """
                    INSERT INTO imtemptrn (
                        ztime, zid, ximtmptrn, xdate, xyear, xper, xdatecom,
                        xrem, xwh, xsign, xaction, zemail, xtrnimt, xsup,
                        xmember, xtyperec, xdateinv, xstatustrn
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """

                cursor.execute(insert_sql, [
                    timezone.now(),
                    current_zid,
                    voucher_number,
                    request.POST.get('xdate'),
                    request.POST.get('xyear'),
                    request.POST.get('xper'),
                    request.POST.get('xdatecom'),
                    request.POST.get('xrem'),
                    request.POST.get('xwh'),
                    1,  # xsign
                    'Receive Entry',  # xaction
                    request.user.username,  # zemail
                    request.POST.get('xtrnimt'),
                    request.POST.get('xsup'),
                    request.POST.get('xmember'),
                    request.POST.get('xtype'),  # xtyperec
                    request.POST.get('xdateinv'),
                    'Open'  # xstatustrn
                ])

                logger.info(f"Voucher {voucher_number} inserted into imtemptrn table by {request.user.username} successfully")

                return JsonResponse({
                    'success': True,
                    'voucher_number': voucher_number
                })

        except Exception as e:
            logger.error(f"Failed to insert voucher {voucher_number}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Database insertion failed',
                'details': str(e)
            }, status=500)

    return JsonResponse({'success': False})

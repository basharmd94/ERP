from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin
from ..models.cacus import Cacus
import logging

logger = logging.getLogger(__name__)

"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class CustomersView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'crossapp_customers'
    template_name = 'customers.html'
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


@login_required
def get_customers_json(request):

    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({'error': 'No business context found'}, status=400)

        # Query customers for the current ZID with specific fields
        customers = Cacus.objects.filter(zid=current_zid).values(
            'xcus',      # Customer Code
            'xshort',
            'xstate',
            'xcity',
            'xmobile',
            'xemail',
            'xtaxnum',

        )

        # Convert Decimal fields to string for JSON serialization
        customers_list = list(customers)
        logger.info(f"Retrieved customers for ZID {current_zid}: {customers_list}")

        return JsonResponse({'customers': customers_list}, safe=False)
    except Exception as e:
        logger.error(f"Error retrieving customers: {str(e)}")
        return JsonResponse({'error': str(e)}, status=404)


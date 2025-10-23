from django.http import JsonResponse
from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.utils.items_check_inventory import items_check_inventory
from apps.authentication.mixins import ModulePermissionMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction, connection
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)



class SalesReturnView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'sales_return'
    template_name = 'sales_return.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


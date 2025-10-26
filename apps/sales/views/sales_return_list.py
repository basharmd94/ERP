from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin
import logging

# Set up logging
logger = logging.getLogger(__name__)



class SalesReturnListView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'sales_return_list'
    template_name = 'sales_return_list.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

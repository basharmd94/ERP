# Django imports
from django.views.generic import TemplateView

# Local application imports
from web_project import TemplateLayout
from apps.authentication.mixins import ModulePermissionMixin, ZidRequiredMixin

# Transaction View
class ReportsView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'acreports'
    template_name = 'reports/acreports.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file

        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin


class DayEndProcessView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'day_end_process'
    template_name = 'day_end_process.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context



# pos Sales
class PosSalesView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'pos_sales'
    template_name = 'pos_sales.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


# Sales List view
class SalesListView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'sales_list'
    template_name = 'sales_list.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Sales Return view
class SalesReturnView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'sales_return'
    template_name = 'sales_return.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


# Sales Return List
class SalesReturnListView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'sales_return_list'
    template_name = 'sales_return_list.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context



# Sales Reports View
class SalesReportsView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'sales_reports'
    template_name = 'reports/sales_reports.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

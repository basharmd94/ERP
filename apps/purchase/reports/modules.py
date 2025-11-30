from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin


class POReportView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'po_reports'
    template_name = 'reports/po_reports.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

# Product Purchase Report
class ProductPurchaseReportView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'po_reports_product_purchase'
    template_name = 'reports/po_reports_product_purchase.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


# Mrr Report By Date
class MrrReportByDateView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'po_reports_mrr_by_date'
    template_name = 'reports/po_reports_mrr_by_date.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context


# Item Wise Mrr Report
class ItemWiseMrrReportView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'po_reports_item_wise'
    template_name = 'reports/po_reports_item_wise.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

# Statement by supplier
class StatementBySupplierView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'po_reports_stat_supplier'
    template_name = 'reports/po_reports_stat_supplier.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

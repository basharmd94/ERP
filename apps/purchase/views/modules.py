from django.views.generic import TemplateView
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin


class POCreateView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'po_create'
    template_name = 'po_create.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

# PO Confirm
class POConfirmView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'po_confirm'
    template_name = 'po_confirm.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

# PO List
class POListView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'po_list'
    template_name = 'po_list.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

# purchase Return
class PurchaseReturnView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'po_return'
    template_name = 'po_return.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context

# Django imports
from django.views.generic import TemplateView

# Local application imports
from web_project import TemplateLayout
from apps.authentication.mixins import ModulePermissionMixin, ZidRequiredMixin

# Transaction View
class TransactionView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'transaction'
    template_name = 'acct_transaction.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file

        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# ======================================================
#  First Column
# ======================================================
# Voucher Entry
class VoucherEntryView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'voucher_entry'
    template_name = 'voucher_entry.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Payment Voucher Entry View
class PaymentVoucherEntryView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'payment_voucher_entry'
    template_name = 'payment_voucher_entry.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Receipt voucher Entry View
class ReceiptVoucherEntryView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'receipt_voucher_entry'
    template_name = 'receipt_voucher_entry.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


# Opening Balance view
class OpeningBalancesView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'opening_balances'
    template_name = 'opening_balances.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# ======================================================
#  Second Column
# ======================================================
# Chart of Accounts View
class ChartOfAccountsView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'chart_of_accounts'
    template_name = 'chart_of_accounts.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Year End Processing View
class YearEndProcessingView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'year_end_processing'
    template_name = 'year_end_processing.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Im to GL Trial Run view
class ImToGlTrialRunView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'im_to_gl_trial_run'
    template_name = 'im_to_gl_trial_run.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Im to GL Final Run View
class ImToGlFinalRunView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'im_to_gl_final_run'
    template_name = 'im_to_gl_final_run.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Im To Gl Audit Trail View
class ImToGlAuditTrailView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'im_to_gl_audit_trail'
    template_name = 'im_to_gl_audit_trail.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Voucher Details Single View
class VoucherDetailsSingleView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'voucher_details_single'
    template_name = 'voucher_details_single.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Voucher Details Month View
class VoucherDetailsMonthView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'voucher_details_month'
    template_name = 'voucher_details_month.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# ======================================================
#  Third Column (Cheque Management)
# ======================================================
# Cheque
class ChequeView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'cheque'
    template_name = 'cheque.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Cheque Register Entry
class ChequeRegisterEntryView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'cheque_register_entry'
    template_name = 'cheque_register_entry.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Cheque Receive Register
class ChequeReceiveRegisterView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'cheque_receive_register'
    template_name = 'cheque_receive_register.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

# Cheque Deposit Entry
class ChequeDepositEntryView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'cheque_deposit_entry'
    template_name = 'cheque_deposit_entry.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

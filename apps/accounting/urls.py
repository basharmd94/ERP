from django.urls import path

# Import all accounting module views from views.modules
from .views.modules import (
    TransactionView,
    VoucherEntryView,
    PaymentVoucherEntryView,
    ReceiptVoucherEntryView,
    OpeningBalancesView,
    ChartOfAccountsView,
    YearEndProcessingView,
    ImToGlTrialRunView,
    ImToGlFinalRunView,
    ImToGlAuditTrailView,
    VoucherDetailsSingleView,
    VoucherDetailsMonthView,
    ChequeView,
    ChequeRegisterEntryView,
    ChequeReceiveRegisterView,
    ChequeDepositEntryView,
)
from .reports.modules import ReportsView

urlpatterns = [
    # +--------------------------------+
    # |   Accounting Transaction URLs  |
    # +--------------------------------+

    # Main Transaction View
    path("transaction/", TransactionView.as_view(), name="acct-transaction"),

    # +--------------------------------+
    # |   First Column - Basic Transactions
    # +--------------------------------+
    path("transaction/voucher-entry/", VoucherEntryView.as_view(), name="voucher-entry"),
    path("transaction/payment-voucher-entry/", PaymentVoucherEntryView.as_view(), name="payment-voucher-entry"),
    path("transaction/receipt-voucher-entry/", ReceiptVoucherEntryView.as_view(), name="receipt-voucher-entry"),
    path("transaction/opening-balances/", OpeningBalancesView.as_view(), name="opening-balances"),

    # +--------------------------------+
    # |   Second Column - Advanced Operations
    # +--------------------------------+
    path("transaction/chart-of-accounts/", ChartOfAccountsView.as_view(), name="chart-of-accounts"),
    path("transaction/year-end-processing/", YearEndProcessingView.as_view(), name="year-end-processing"),
    path("transaction/im-to-gl-trial-run/", ImToGlTrialRunView.as_view(), name="im-to-gl-trial-run"),
    path("transaction/im-to-gl-final-run/", ImToGlFinalRunView.as_view(), name="im-to-gl-final-run"),
    path("transaction/im-to-gl-audit-trail/", ImToGlAuditTrailView.as_view(), name="im-to-gl-audit-trail"),
    path("transaction/voucher-details-single/", VoucherDetailsSingleView.as_view(), name="voucher-details-single"),
    path("transaction/voucher-details-month/", VoucherDetailsMonthView.as_view(), name="voucher-details-month"),

    # +--------------------------------+
    # |   Third Column - Cheque Management
    # +--------------------------------+
    path("transaction/cheque/", ChequeView.as_view(), name="cheque"),
    path("transaction/cheque-register-entry/", ChequeRegisterEntryView.as_view(), name="cheque-register-entry"),
    path("transaction/cheque-receive-register/", ChequeReceiveRegisterView.as_view(), name="cheque-receive-register"),
    path("transaction/cheque-deposit-entry/", ChequeDepositEntryView.as_view(), name="cheque-deposit-entry"),

    # +--------------------------------+
    # |   REPORTS-ACCOUNTING
    # +--------------------------------+
    path("reports/", ReportsView.as_view(), name="reports"),

]

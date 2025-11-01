from django.urls import path
from .views.pos_sales import SalesView, pos_complete_sale
from .views.pos_print import pos_print_slip
from .views.sales_list import SalesListView
from .views.sales_item_list import sales_item_list_ajax
from .views.print_invoice import print_invoice
from .views.todays_sales import todays_sales_ajax, todays_sales_summary
from .views.edit_sales import SalesEditView
from .views.edit_sales_api import update_transaction_api, delete_transaction_api
from .views.day_end_process import DayEndProcess, create_day_end_process, delete_day_end_process
from .views.sales_return import SalesReturnView
from .views.sales_return_confirm import sales_return_confirm
from .views.sales_return_detail import SalesReturnDetailView
from .views.sales_return_print import sales_return_print
from .views.sales_return_export_excel import SalesReturnExcelExportView
from .views.sales_return_list import SalesReturnListView
from .views.sales_return_item_list import sales_return_item_list
from .views.sales_return_delete import sales_return_delete
from .views.sales_return_update import SalesReturnUpdateView
from .views.reports.sales_reports import SalesReportsView
from .views.reports.daily_sales_report import DailySalesReportsView
from .views.reports.daily_sales_report_export import daily_sales_report_export



urlpatterns = [
     # +--------------------------+
    # |   Sales Main Page URLS   |
    # +--------------------------+
    path("pos-sales/", SalesView.as_view(), name="pos-sales"),
    # Sales List
    path("sales-list/", SalesListView.as_view(), name="sales-list"),
    # Edit sales
    path("edit-sales/<str:transaction_id>/", SalesEditView.as_view(), name="edit-sales"),
    # +--------------------------+
    # |   Day End Process URLS   |
    # +--------------------------+
    path("day-end-process/", DayEndProcess.as_view(), name="day-end-process"),
    path("create-day-end-process/", create_day_end_process, name="create-day-end-process"),
    # create a block comment Sales Return URLs
    path("api/delete-day-end-process/<str:date>/", delete_day_end_process, name="delete-day-end-process"),
    # AJAX API endpoints
    path("api/pos/complete-sale/", pos_complete_sale, name="pos-complete-sale"),
    path("api/sales-item-list/", sales_item_list_ajax, name="sales-item-list-ajax"),
    path("api/todays-sales/", todays_sales_ajax, name="todays-sales-ajax"),
    path("api/todays-sales-summary/", todays_sales_summary, name="todays-sales-summary"),
    # Edit sales API endpoints
    path("api/update-transaction/", update_transaction_api, name="update-transaction-api"),
    path("api/delete-transaction/", delete_transaction_api, name="delete-transaction-api"),
    # invoice print
    path("print-invoice/<str:transaction_id>/", print_invoice, name="print-invoice"),
    # slip print
    path("pos/print-slip/<str:transaction_id>/", pos_print_slip, name="pos-print-slip"),

    # +--------------------------+
    # |   Sales Return URLS      |
    # +--------------------------+
    # Sales return Main Page URL
    path("sales-return/", SalesReturnView.as_view(), name="sales-return"),
    # sales Return Confirm
    path("sales-return-confirm/", sales_return_confirm, name="sales-return-confirm"),
    # sales Return List Class base view for showing menu
    path("sales-return-list/", SalesReturnListView.as_view(), name="sales-return-list"),
    # sales Return Item List API ajax endpoint
    path("api/sales-return-item-list/", sales_return_item_list, name="sales-return-item-list"),
    # Sales Return Detail
    path("sales-return-detail/<str:transaction_id>/", SalesReturnDetailView.as_view(), name="sales-return-detail"),
    # sales return edit
    path("sales-return-update/<str:transaction_id>/", SalesReturnUpdateView.as_view(), name="sales-return-update"),
    # print/export sales return
    path("sales-return-print/<str:transaction_id>/", sales_return_print, name="sales-return-print"),
    # sales return delete
    path("api/sales-return-delete/<str:transaction_id>/", sales_return_delete, name="sales-return-delete"),
    # sales return export excel
    path("sales-return-export-excel/<str:transaction_id>/", SalesReturnExcelExportView.as_view(), name="sales-return-export-excel"),

    # +--------------------------+
    # |  Sales Reports URLS      |
    # +--------------------------+
    # Sales Reports Main Page
    path("reports/", SalesReportsView.as_view(), name="sales-reports"),
    # Daily Sales Reports
    path("reports/daily-sales-report/", DailySalesReportsView.as_view(), name="daily-sales-report"),

    # Individual Report URLs
    # Daily Sales Report Export (PDF/Excel)
    path("reports/daily-sales-report-export/", daily_sales_report_export, name="daily-sales-report-export"),


]

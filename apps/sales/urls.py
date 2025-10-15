from django.urls import path
from .views.pos_sales import SalesView, pos_complete_sale
from .views.pos_print import pos_print_slip
from .views.sales_list import SalesListView
from .views.sales_item_list import sales_item_list_ajax
from .views.print_invoice import print_invoice
from .views.todays_sales import todays_sales_ajax, todays_sales_summary
from .views.edit_sales import SalesEditView
from .views.edit_sales_api import update_transaction_api, delete_transaction_api


urlpatterns = [
    # Sales Management URLs
    path("pos-sales/", SalesView.as_view(), name="pos-sales"),
    path("sales-list/", SalesListView.as_view(), name="sales-list"),
    # edit sales
    path("edit-sales/<str:transaction_id>/", SalesEditView.as_view(), name="edit-sales"),


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


]

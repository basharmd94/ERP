from django.urls import path
from .views.pos_sales import SalesView, pos_complete_sale
from .views.pos_print import pos_print_slip
from .views.sales_list import SalesListView
from .views.sales_item_list import sales_item_list_ajax
from .views.print_invoice import print_invoice
from .views.todays_sales import todays_sales_ajax, todays_sales_summary



urlpatterns = [
    # Sales Management URLs
    path("pos-sales/", SalesView.as_view(), name="pos-sales"),
    path("sales-list/", SalesListView.as_view(), name="sales-list"),


    # AJAX API endpoints
    path("api/pos/complete-sale/", pos_complete_sale, name="pos-complete-sale"),
    path("api/sales-item-list/", sales_item_list_ajax, name="sales-item-list-ajax"),
    path("api/todays-sales/", todays_sales_ajax, name="todays-sales-ajax"),
    path("api/todays-sales-summary/", todays_sales_summary, name="todays-sales-summary"),
    # invoice print
    path("print-invoice/<str:transaction_id>/", print_invoice, name="print-invoice"),
    # slip print
    path("pos/print-slip/<str:transaction_id>/", pos_print_slip, name="pos-print-slip"),


]

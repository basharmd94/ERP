from django.urls import path
from .views.pos_sales import SalesView, pos_products_api, pos_complete_sale
from .views.pos_print import pos_print_slip


urlpatterns = [
    # Sales Management URLs
    path("pos-sales/", SalesView.as_view(), name="pos-sales"),

    # AJAX API endpoints
    path("api/pos/products/", pos_products_api, name="pos-products-api"),
    path("api/pos/complete-sale/", pos_complete_sale, name="pos-complete-sale"),

    # Print URLs
    path("pos/print-slip/<str:transaction_id>/", pos_print_slip, name="pos-print-slip"),

]

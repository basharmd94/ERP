from django.urls import path
from .views.pos_sales import SalesView, pos_products_api, pos_complete_sale


urlpatterns = [
    # Sales Management URLs
    path("pos-sales/", SalesView.as_view(), name="pos-sales"),
    
    # AJAX API endpoints
    path("api/pos/products/", pos_products_api, name="pos-products-api"),
    path("api/pos/complete-sale/", pos_complete_sale, name="pos-complete-sale"),
]

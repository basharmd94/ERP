from django.urls import path
from .views.pos_products_api import pos_products_api
from .views.avg_item_price import avg_item_price
from .views.api_get_warehouse import api_get_warehouse
from .views.api_get_supplier import api_get_supplier



urlpatterns = [
    path('pos/products/', pos_products_api, name='pos_products_api'),
    path('avg-item-price/', avg_item_price, name='avg-item-price'),
    # get warehouse list
    path('get-warehouse/', api_get_warehouse, name='api-get-warehouse'),
    # get supplier list
    path('get-supplier/', api_get_supplier, name='api-get-supplier'),
]

from django.urls import path
from .views.pos_products_api import pos_products_api
from .views.avg_item_price import avg_item_price
from .views.api_get_warehouse import api_get_warehouse
from .views.api_get_supplier import api_get_supplier
from .views.get_current_zid import get_current_zid_api



urlpatterns = [
    path('pos/products/', pos_products_api, name='pos_products_api'),
    path('avg-item-price/', avg_item_price, name='avg-item-price'),
    # get warehouse list
    path('get-warehouse/', api_get_warehouse, name='api-get-warehouse'),
    # get supplier list
    path('get-supplier/', api_get_supplier, name='api-get-supplier'),

     path("get-current-zid/", get_current_zid_api, name="get-current-zid-api"),
]

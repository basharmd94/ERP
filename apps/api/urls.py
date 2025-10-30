from django.urls import path
from .views.pos_products_api import pos_products_api
from .views.avg_item_price import avg_item_price
from .views.api_get_warehouse import api_get_warehouse
from .views.api_get_supplier import api_get_supplier
from .views.get_current_zid import get_current_zid_api
from .views.api_get_project import api_get_project
from .views.api_get_customer import api_get_customer
from .views.api_get_xcodes import api_get_xcodes



urlpatterns = [

    # +--------------------------+
    # |  Item Related URLS      |
    # +--------------------------+
    path('pos/products/', pos_products_api, name='pos_products_api'),
    # avg item price
    path('avg-item-price/', avg_item_price, name='avg-item-price'),

    # Generic xcode endpoint - handles all xcode types
    path('xcodes/<str:xtype>/', api_get_xcodes, name='api-get-xcodes'),

    # get warehouse list
    path('get-warehouse/', api_get_warehouse, name='api-get-warehouse'),
    # get project list
    path('get-project/', api_get_project, name='api-get-project'),
    # get supplier list
    path('get-supplier/', api_get_supplier, name='api-get-supplier'),

    # get customer list
    path('get-customer/', api_get_customer, name='api-get-customer'),

     path("get-current-zid/", get_current_zid_api, name="get-current-zid-api"),
]

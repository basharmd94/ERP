from django.urls import path
from .views.pos_products_api import pos_products_api


urlpatterns = [
    path('pos/products/', pos_products_api, name='pos_products_api'),
    
]

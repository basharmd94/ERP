from django.urls import path
from .views.items import ItemsView, get_items_json, delete_item_api
from .views.brands import BrandsView, get_brands_json, create_brand_api, update_brand_api, delete_brand_api
from .views.customers import CustomersView, get_customers_json
from .views.item_group import ItemGroupView, get_item_group_json, create_item_group_api, update_item_group_api, delete_item_group_api



urlpatterns = [
    # Items
    path("items/",ItemsView.as_view(template_name="items.html"),name="crossapp-items"),
    # Brands
    path("xcodes/brands/",BrandsView.as_view(template_name="brands.html"), name="brands"),
    # Item groups/ Category
    path("xcodes/item_group/", ItemGroupView.as_view(template_name="item_group.html"), name="item_group"),

    # Customers
    path("customers/", CustomersView.as_view(template_name="customers.html"), name="crossapp-customers"),

    # Suppliers
    path("suppliers/", ItemsView.as_view(template_name="crossapp/suppliers/suppliers.html"), name="crossapp-suppliers"),

    # Common Codes
    path("common-codes/", ItemsView.as_view(template_name="crossapp/common-codes/common-codes.html"), name="crossapp-common-codes"),


    # Ajax Requst URL
    # get items data as json by using Ajax request
        # get customers data as json
    path("api/customers/", get_customers_json, name="crossapp-customers-api"),
    path( "api/items/", get_items_json, name="crossapp-items-api"),
    path ("api/items/delete/<str:item_code>/", delete_item_api, name="delete-item-api"),
    # get all brands data as json by using Ajax request
    path( "api/brands/", get_brands_json, name="crossapp-brands-api"),
    path ("api/brands/create/", create_brand_api, name="create-brand-api"),
    path ("api/brands/update/<str:brand_code>/", update_brand_api, name="update-brand-api"),
    path ("api/brands/delete/<str:brand_code>/", delete_brand_api, name="delete-brand-api"),

    # Item Group URLs
    path('api/item_group/', get_item_group_json, name='get-item-group'),
    path('api/item_group/create/', create_item_group_api, name='create-item-group-api'),
    path('api/item_group/update/<str:item_group_code>/', update_item_group_api, name='update-item-group-api'),
    path('api/item_group/delete/<str:item_group_code>/', delete_item_group_api, name='delete-item-group-api'),



]

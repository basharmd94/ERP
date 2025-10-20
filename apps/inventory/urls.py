from django.urls import path
from .views.transaction import TransactionView
from .views.item_ledger import ItemLedgerView
from .views.item_ledger import get_item_ledger
from .views.receive_entry import ReceiveEntryView, save_receive_entry
from .views.receive_entry_list import receive_entry_list_ajax
from .views.last_10_orders import last_10_orders




urlpatterns = [
    # path('', inventory_items, name='inventory-items'),
    path("transaction/", TransactionView.as_view(template_name="transaction.html"), name="inventory-transaction"),
    # item-leger
    path("reports/item-ledger/", ItemLedgerView.as_view(template_name = "item_ledger.html"), name="item-ledger"),

    # get item ledger information data by warehouse, from date, to date, item code
    path("reports/item-ledger/get-item-ledger/", get_item_ledger, name="get-item-ledger"),
    # receive entry
    path("transaction/receive-entry/", ReceiveEntryView.as_view(template_name="receive_entry.html"), name="receive-entry"),
    # receive entry list AJAX endpoint
    path("api/receive_entry_list/", receive_entry_list_ajax, name="receive-entry-list-ajax"),
    # save receive entry
    path("api/save_receive_entry/", save_receive_entry, name="save-receive-entry"),
    # API endpoint for Smart Item Selector


    # get last 10 order from opodt table for report
    path("reports/last-10-orders/", last_10_orders, name="last-10-orders"),


]

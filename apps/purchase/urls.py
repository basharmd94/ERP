from django.urls import path

from .views.modules import PurchaseOrderView,  POConfirmView, POListView, PurchaseReturnView
from .reports.modules import (
    POReportView, ProductPurchaseReportView, MrrReportByDateView,
    ItemWiseMrrReportView, StatementBySupplierView)

from .views.po_create import po_create # Purchase Order Create function
from .views.po_open_list import po_open_list # Show Purchase Open List in Confirm GRN/MRR Page
from .views.po_confirm import po_confirm # Purchase Order Confirm function
from .reports.po_req_print import po_req_print # Purchase Requisition Print function
from .reports.po_grn_print import po_grn_print # Purchase/GRN Print function
from .views.po_delete import po_delete # Delete Purchase order using Po number



urlpatterns = [
    # +--------------------------+
    # |   Purchase Menu List     |
    # +--------------------------+

    # Purchase Order Page
    path('purchase-order/', PurchaseOrderView.as_view(), name='purchase-order'),

    # Purchase Order Create function
    path('po-create/', po_create, name='po-create'),

    # Purchase Requisition Print function
    path('po-req-print/<str:transaction_id>/', po_req_print, name='po-req-print'),

    # Show Purchase Open List in Confirm GRN/MRR Page
    path('po-open-list/', po_open_list, name='po-open-list'),

    # Purchase Confirm Page
    path('po-confirm/', POConfirmView.as_view(), name='po-confirm'),

    # purchase order confirm
    path('po-confirm/<str:transaction_id>/', po_confirm, name='po-confirm-detail'),

    # Purchase/GRN Print
    path('po-grn-print/<str:transaction_id>/', po_grn_print, name='po-grn-print'),

    # Delete Purchase  order using Po number
    path('po-delete/<str:po_number>/', po_delete, name='po-delete'),

    path('po-list/', POListView.as_view(), name='po-list'),
    # +--------------------------+
    # |   Purchase Return URLS   |
    # +--------------------------+
    path('po-return/', PurchaseReturnView.as_view(), name='po-return'),

    # +--------------------------+
    # |   Purchase Reports URLS  |
    # +--------------------------+
    path('po-reports/', POReportView.as_view(), name='po-reports'),

    # +--------------------------+
    # |  Individual Report URLs  |
    # +--------------------------+
    path('po-reports-product-purchase/', ProductPurchaseReportView.as_view(), name='po-reports-product-purchase'),
    path('po-reports-mrr-date/', MrrReportByDateView.as_view(), name='po-reports-mrr-date'),
    path('po-reports-item-wise/', ItemWiseMrrReportView.as_view(), name='po-reports-item-wise'),
    path('po-reports-stat-supplier/', StatementBySupplierView.as_view(), name='po-reports-stat-supplier'),
]

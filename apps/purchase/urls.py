from django.urls import path

from .views.modules import PurchaseOrderView,  POConfirmView, POListView, PurchaseReturnView
from .reports.modules import (
    POReportView, ProductPurchaseReportView, MrrReportByDateView,
    ItemWiseMrrReportView, StatementBySupplierView)

from .views.po_create import po_create # Purchase Order Create function

urlpatterns = [
    # +--------------------------+
    # |   Purchase Menu List     |
    # +--------------------------+

    # Purchase Order Page
    path('purchase-order/', PurchaseOrderView.as_view(), name='purchase-order'),

    # Purchase Order Create function
    path('po-create/', po_create, name='po-create'),

    # Purchase Order Create view
    path('po-confirm/', POConfirmView.as_view(), name='po-confirm'),
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

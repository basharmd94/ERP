from django.urls import path

from .views.modules import POCreateView, POConfirmView, POListView, PurchaseReturnView
from .reports.modules import POReportView, ProductPurchaseReportView, MrrReportByDateView, ItemWiseMrrReportView, StatementBySupplierView

"""
### Url-pattern-slug
po-create
po-confirm
po-list
po-return
po-reports
po-reports-product-purchase
po-reports-mrr-date
po-reports-item-wise
po-reports-stat-supplier
"""

urlpatterns = [
    path('po-create', POCreateView.as_view(), name='po-create'),
    path('po-confirm', POConfirmView.as_view(), name='po-confirm'),
    path('po-list', POListView.as_view(), name='po-list'),
    path('po-return', PurchaseReturnView.as_view(), name='po-return'),
    path('po-reports', POReportView.as_view(), name='po-reports'),
    path('po-reports-product-purchase', ProductPurchaseReportView.as_view(), name='po-reports-product-purchase'),
    path('po-reports-mrr-date', MrrReportByDateView.as_view(), name='po-reports-mrr-date'),
    path('po-reports-item-wise', ItemWiseMrrReportView.as_view(), name='po-reports-item-wise'),
    path('po-reports-stat-supplier', StatementBySupplierView.as_view(), name='po-reports-stat-supplier'),
]

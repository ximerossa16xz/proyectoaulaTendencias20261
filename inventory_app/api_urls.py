from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    CategoryListCreateView,
    CategoryDetailView,
    InventoryMovementDetailView,
    InventoryMovementListCreateView,
    SupplierListCreateView,
    SupplierDetailView,
    WarehouseListCreateView,
    WarehouseDetailView,
    ProductWarehouseStockListCreateView,
    ProductWarehouseStockDetailView,
    RestockOrderListCreateView,
    RestockOrderDetailView,
    LowStockAlertView,
    InventoryValorizationReportView,
    MovementsPeriodReportView,
    ProductRotationRankingView,
    BulkInventoryAdjustmentView
)

urlpatterns = [
    path('products/', ProductListCreateView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('products/alerts/low-stock/', LowStockAlertView.as_view()),
    path('categories/', CategoryListCreateView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),
    path('suppliers/', SupplierListCreateView.as_view()),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view()),
    path('warehouses/', WarehouseListCreateView.as_view()),
    path('warehouses/<int:pk>/', WarehouseDetailView.as_view()),
    path('warehouse-stocks/', ProductWarehouseStockListCreateView.as_view()),
    path('warehouse-stocks/<int:pk>/', ProductWarehouseStockDetailView.as_view()),
    path('movements/', InventoryMovementListCreateView.as_view()),
    path('movements/<int:pk>/', InventoryMovementDetailView.as_view()),
    path('restock-orders/', RestockOrderListCreateView.as_view()),
    path('restock-orders/<int:pk>/', RestockOrderDetailView.as_view()),
    
    # Reportes
    path('reports/valuation/', InventoryValorizationReportView.as_view(), name='report-valuation'),
    path('reports/movements/', MovementsPeriodReportView.as_view(), name='report-movements'),
    path('reports/rotation/', ProductRotationRankingView.as_view(), name='report-rotation'),
    
    # Ajuste masivo
    path('adjustments/bulk/', BulkInventoryAdjustmentView.as_view(), name='bulk-adjustment'),
]

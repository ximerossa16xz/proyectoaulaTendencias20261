from django.urls import path
from .views import (
    ProductListCreateView,
    ProductDetailView,
    CategoryListCreateView,
    CategoryDetailView,
    SupplierListCreateView,
    SupplierDetailView,
    RestockOrderListCreateView,
    LowStockAlertView
)

urlpatterns = [
    path('products/', ProductListCreateView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('categories/', CategoryListCreateView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),
    path('suppliers/', SupplierListCreateView.as_view()),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view()),
    path('restock-orders/', RestockOrderListCreateView.as_view()),
    path('products/alerts/low-stock/', LowStockAlertView.as_view()),
]
from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    SupplierListCreateView, SupplierDetailView,
    ProductListCreateView, ProductDetailView,
    LowStockAlertView, UpdateProductStockView
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    path('suppliers/', SupplierListCreateView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='supplier-detail'),

    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/update-stock/', UpdateProductStockView.as_view(), name='update-stock'),
    path('products/alerts/low-stock/', LowStockAlertView.as_view(), name='low-stock-alert'),
]
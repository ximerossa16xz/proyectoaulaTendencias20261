from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    SupplierListCreateView, SupplierDetailView,
    ProductListCreateView, ProductDetailView,
    RestockOrderListCreateView, RestockOrderDetailView
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    path('suppliers/', SupplierListCreateView.as_view(), name='supplier-list-create'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='supplier-detail'),

    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    path('restock-orders/', RestockOrderListCreateView.as_view(), name='restock-list-create'),
    path('restock-orders/<int:pk>/', RestockOrderDetailView.as_view(), name='restock-detail'),
]
from django.urls import path
from .views import (
    dashboard_view,
    inventory_view,
    products_view,
    categories_view,
    suppliers_view,
    movements_view,
    restock_view,
    alerts_view
)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('inventory/', inventory_view, name='inventory'),

    path('inventory/products/', products_view, name='products'),
    path('inventory/categories/', categories_view, name='categories'),
    path('inventory/suppliers/', suppliers_view, name='suppliers'),
    path('inventory/movements/', movements_view, name='movements'),
    path('inventory/restock/', restock_view, name='restock'),
    path('inventory/alerts/', alerts_view, name='alerts'),
]

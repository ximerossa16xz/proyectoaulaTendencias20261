from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, InventoryMovement, Product, RestockOrder, Supplier
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    InventoryMovementSerializer,
    ProductSerializer,
    RestockOrderSerializer,
    SupplierSerializer,
)


@login_required
def dashboard_view(request):
    return render(request, 'inventory_app/index.html')


@login_required
def inventory_view(request):
    return render(request, 'inventory_app/inventory.html')


@login_required
def movements_view(request):
    return render(request, 'inventory_app/movements.html')


@login_required
def restock_view(request):
    return render(request, 'inventory_app/restock.html')


@login_required
def products_view(request):
    return render(request, 'inventory_app/products.html')


@login_required
def categories_view(request):
    return render(request, 'inventory_app/categories.html')


@login_required
def suppliers_view(request):
    return render(request, 'inventory_app/suppliers.html')


@login_required
def alerts_view(request):
    return render(request, 'inventory_app/alerts.html')


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Category.objects.annotate(product_count=models.Count('product')).order_by('name')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return Category.objects.annotate(product_count=models.Count('product')).order_by('name')


class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.order_by('name')
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.order_by('name')
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return Product.objects.select_related('category', 'supplier').order_by('name')


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category', 'supplier').order_by('name')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class InventoryMovementListCreateView(generics.ListCreateAPIView):
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return InventoryMovement.objects.select_related('product', 'user').order_by('-timestamp')

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)


class InventoryMovementDetailView(generics.RetrieveAPIView):
    queryset = InventoryMovement.objects.select_related('product', 'user').order_by('-timestamp')
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class RestockOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = RestockOrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return RestockOrder.objects.select_related('supplier', 'product', 'created_by').order_by('-created_at')

    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)


class RestockOrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = RestockOrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return RestockOrder.objects.select_related('supplier', 'product', 'created_by').order_by('-created_at')

    def perform_update(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)


class LowStockAlertView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return Product.objects.select_related('category', 'supplier').filter(
            stock__lt=models.F('minimum_stock')
        ).order_by('stock', 'name')


class UpdateProductStockView(generics.UpdateAPIView):
    queryset = Product.objects.select_related('category', 'supplier').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def patch(self, request, *args, **kwargs):
        product = self.get_object()
        stock = request.data.get('stock')

        if stock is None:
            return Response(
                {'detail': 'El campo "stock" es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            stock = int(stock)
            if stock < 0:
                return Response(
                    {'detail': 'El stock no puede ser negativo.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            product.stock = stock
            product.save()
            serializer = self.get_serializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {'detail': 'El campo "stock" debe ser un número entero.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DjangoValidationError as exc:
            return Response(
                exc.message_dict if hasattr(exc, 'message_dict') else {'detail': exc.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

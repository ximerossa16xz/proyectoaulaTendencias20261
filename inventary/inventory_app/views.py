from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from .permissions import IsAdminOrReadOnly
from .models import Category, Supplier, Product, RestockOrder
from .serializers import CategorySerializer, SupplierSerializer, ProductSerializer, RestockOrderSerializer


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class RestockOrderListCreateView(generics.ListCreateAPIView):
    queryset = RestockOrder.objects.all()
    serializer_class = RestockOrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def perform_create(self, serializer):
        # Assign the current user as created_by
        serializer.save(created_by=self.request.user)


class RestockOrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = RestockOrder.objects.all()
    serializer_class = RestockOrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class LowStockAlertView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return Product.objects.filter(stock__lt=models.F('minimum_stock'))


class UpdateProductStockView(generics.UpdateAPIView):
    queryset = Product.objects.all()
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
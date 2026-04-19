from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
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
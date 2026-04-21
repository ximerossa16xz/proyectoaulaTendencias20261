from rest_framework import serializers
from .models import Category, Supplier, Product, RestockOrder

class CategorySerializer(serializers.ModelSerializer):
    class Meta:

        model = Category

        fields = '__all__'
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:

        model = Supplier

        fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    class Meta:

        model = Product

        fields = '__all__'


class RestockOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = RestockOrder
        fields = ['id', 'supplier', 'supplier_name', 'product', 'product_name', 'product_sku',
                  'quantity', 'status', 'created_at', 'created_by', 'created_by_username', 'received_at']
        read_only_fields = ['id', 'created_at', 'created_by', 'received_at']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
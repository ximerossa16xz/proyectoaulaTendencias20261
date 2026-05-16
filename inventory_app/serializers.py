from rest_framework import serializers
from .models import Category, Supplier, Product, RestockOrder, InventoryMovement

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'status', 'product_count']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'category_name', 'supplier', 'supplier_name',
            'unit_measure', 'cost_price', 'sale_price', 'stock', 'minimum_stock'
        ]

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Stock cannot be negative.')
        return value

    def validate_minimum_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Minimum stock cannot be negative.')
        return value

    def validate(self, attrs):
        cost_price = attrs.get('cost_price', getattr(self.instance, 'cost_price', None))
        sale_price = attrs.get('sale_price', getattr(self.instance, 'sale_price', None))

        if cost_price is not None and sale_price is not None and sale_price < cost_price:
            raise serializers.ValidationError({'sale_price': 'Sale price cannot be lower than cost price.'})

        return attrs


class InventoryMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = InventoryMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type', 'quantity',
            'user', 'user_username', 'timestamp'
        ]
        read_only_fields = ['id', 'user', 'user_username', 'timestamp', 'product_name']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0.')
        return value


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

    def validate(self, attrs):
        supplier = attrs.get('supplier', getattr(self.instance, 'supplier', None))
        product = attrs.get('product', getattr(self.instance, 'product', None))

        if supplier and product and product.supplier_id != supplier.id:
            raise serializers.ValidationError({
                'product': 'Selected product does not belong to the selected supplier.'
            })

        return attrs

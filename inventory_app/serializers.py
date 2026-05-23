from rest_framework import serializers
from django.db import models
from .models import Category, Supplier, Product, RestockOrder, InventoryMovement, Warehouse, ProductWarehouseStock


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'code', 'location', 'capacity', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProductWarehouseStockSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    warehouse_code = serializers.CharField(source='warehouse.code', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    product_total_stock = serializers.IntegerField(source='product.stock', read_only=True)
    stock_available = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductWarehouseStock
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'product_total_stock', 'warehouse', 'warehouse_name',
            'warehouse_code', 'stock', 'stock_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_stock_available(self, obj):
        """Calcula el stock disponible para esta asignación"""
        other_stocks = obj.product.warehouse_stocks.exclude(id=obj.id).aggregate(
            total=models.Sum('stock')
        )['total'] or 0
        return obj.product.stock - other_stocks

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Stock cannot be negative.')
        return value

    def validate(self, attrs):
        product = attrs.get('product') or self.instance.product
        warehouse = attrs.get('warehouse') or self.instance.warehouse
        new_stock = attrs.get('stock', self.instance.stock if self.instance else 0)
        
        # Calcular stock ya asignado en otras bodegas
        other_stocks = product.warehouse_stocks.exclude(id=self.instance.id if self.instance else None).aggregate(
            total=models.Sum('stock')
        )['total'] or 0
        
        total_allocated = other_stocks + new_stock
        
        if total_allocated > product.stock:
            available = product.stock - other_stocks
            raise serializers.ValidationError({
                'stock': f'Stock asignado no puede exceder el disponible. Total disponible: {available}. '
                        f'Stock ya asignado en otras bodegas: {other_stocks}.'
            })
        
        return attrs


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
    primary_warehouse_name = serializers.CharField(source='primary_warehouse.name', read_only=True)
    warehouse_stocks = ProductWarehouseStockSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category', 'category_name', 'supplier', 'supplier_name',
            'primary_warehouse', 'primary_warehouse_name', 'unit_measure', 'cost_price', 
            'sale_price', 'stock', 'minimum_stock', 'warehouse_stocks'
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
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = InventoryMovement
        fields = [
            'id', 'product', 'product_name', 'warehouse', 'warehouse_name', 'movement_type', 
            'quantity', 'user', 'user_username', 'timestamp'
        ]
        read_only_fields = ['id', 'user', 'user_username', 'timestamp', 'product_name', 'warehouse_name']

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


class BulkAdjustmentItemSerializer(serializers.Serializer):
    """Serializer para un item individual en ajuste masivo"""
    product_id = serializers.IntegerField()
    new_stock = serializers.IntegerField(min_value=0)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError('Producto no encontrado.')
        return value


class BulkInventoryAdjustmentSerializer(serializers.Serializer):
    """Serializer para ajuste masivo de inventario"""
    adjustments = BulkAdjustmentItemSerializer(many=True)
    reason = serializers.CharField(max_length=500)

    def validate_adjustments(self, value):
        if not value:
            raise serializers.ValidationError('Debe proporcionar al menos un ajuste.')
        if len(value) > 100:
            raise serializers.ValidationError('Máximo 100 productos por ajuste.')
        
        # Verificar que no haya duplicados
        product_ids = [item['product_id'] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError('Hay productos duplicados en el ajuste.')
        
        return value

    def validate_reason(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('La razón del ajuste es requerida.')
        return value

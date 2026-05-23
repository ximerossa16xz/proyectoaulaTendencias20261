from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class Warehouse(models.Model):
    """Modelo para almacenar ubicaciones/bodegas"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    location = models.CharField(max_length=200)
    capacity = models.IntegerField()  # Capacidad máxima
    status = models.CharField(
        max_length=15,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('maintenance', 'Maintenance')
        ],
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        default='active'
    )

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    nit = models.CharField(max_length=50, unique=True)
    contact = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    primary_warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_products')
    unit_measure = models.CharField(max_length=50)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()  # Stock total agregado de todas las bodegas
    minimum_stock = models.IntegerField()

    def __str__(self):
        return self.name

    def clean(self):
        errors = {}
        if self.stock < 0:
            errors['stock'] = 'Stock cannot be negative.'
        if self.minimum_stock < 0:
            errors['minimum_stock'] = 'Minimum stock cannot be negative.'
        if self.sale_price < self.cost_price:
            errors['sale_price'] = 'Sale price cannot be lower than cost price.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ProductWarehouseStock(models.Model):
    """Modelo para almacenar stock por producto por bodega"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='warehouse_stocks')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='product_stocks')
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'warehouse')
        ordering = ['warehouse__name']

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.stock} units"

    def clean(self):
        if self.stock < 0:
            raise ValidationError({'stock': 'Stock cannot be negative.'})
        
        # Validar que la suma de warehouse_stocks no exceda el stock total del producto
        # Excluir el actual si es una actualización
        other_stocks = self.product.warehouse_stocks.exclude(id=self.id).aggregate(
            total=models.Sum('stock')
        )['total'] or 0
        
        total_allocated = other_stocks + self.stock
        
        if total_allocated > self.product.stock:
            raise ValidationError({
                'stock': f'La suma de stocks en bodegas no puede exceder el stock total ({self.product.stock}). '
                         f'Stock ya asignado: {other_stocks}. Stock disponible: {self.product.stock - other_stocks}.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # NO recalcular el stock total del producto
        # El stock del producto es independiente de la distribución en bodegas


class InventoryMovement(models.Model):
    MOVEMENT_TYPE_PURCHASE = 'purchase'
    MOVEMENT_TYPE_RETURN = 'return'
    MOVEMENT_TYPE_SALE = 'sale'
    MOVEMENT_TYPE_ADJUSTMENT = 'adjustment'
    MOVEMENT_TYPE_DISPOSAL = 'disposal'

    INBOUND_TYPES = {MOVEMENT_TYPE_PURCHASE, MOVEMENT_TYPE_RETURN}
    OUTBOUND_TYPES = {MOVEMENT_TYPE_SALE, MOVEMENT_TYPE_ADJUSTMENT, MOVEMENT_TYPE_DISPOSAL}
    MOVEMENT_TYPE_CHOICES = [
        (MOVEMENT_TYPE_PURCHASE, 'Purchase'),
        (MOVEMENT_TYPE_RETURN, 'Return'),
        (MOVEMENT_TYPE_SALE, 'Sale'),
        (MOVEMENT_TYPE_ADJUSTMENT, 'Adjustment'),
        (MOVEMENT_TYPE_DISPOSAL, 'Disposal'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_movements')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='inventory_movements')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.product.name} - {self.movement_type} ({self.quantity})'

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than 0.'})

    def get_stock_delta(self):
        if self.movement_type in self.INBOUND_TYPES:
            return self.quantity
        return -self.quantity

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.pk:
            return super().save(*args, **kwargs)

        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=self.product_id)
            delta = self.get_stock_delta()
            
            if self.warehouse:
                # Actualizar stock por bodega
                warehouse_stock, _ = ProductWarehouseStock.objects.select_for_update().get_or_create(
                    product=product,
                    warehouse=self.warehouse
                )
                new_warehouse_stock = warehouse_stock.stock + delta
                
                if new_warehouse_stock < 0:
                    raise ValidationError({'quantity': f'This movement would leave negative stock in {self.warehouse.name}.'})
                
                warehouse_stock.stock = new_warehouse_stock
                warehouse_stock.save(update_fields=['stock'])
            
            # Siempre actualizar stock total
            new_stock = product.stock + delta

            if new_stock < 0:
                raise ValidationError({'quantity': 'This movement would leave the product with negative stock.'})

            product.stock = new_stock
            product.save(update_fields=['stock'])
            return super().save(*args, **kwargs)


class RestockOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='restock_orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='restock_orders')
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='restock_orders')
    received_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"RestockOrder {self.id} - {self.product.name} ({self.quantity} units)"

    def save(self, *args, **kwargs):
        self.full_clean()

        old_status = None
        if self.pk:
            old_status = RestockOrder.objects.only('status').get(pk=self.pk).status

        with transaction.atomic():
            if self.status == 'received' and old_status != 'received':
                product = Product.objects.select_for_update().get(pk=self.product_id)
                product.stock += self.quantity
                product.save(update_fields=['stock'])
                self.received_at = self.received_at or timezone.now()
            elif self.status != 'received' and not self.pk:
                self.received_at = None

            return super().save(*args, **kwargs)

    def clean(self):
        errors = {}
        if self.quantity <= 0:
            errors['quantity'] = 'Quantity must be greater than 0.'
        if self.status == 'received' and not self.received_at:
            self.received_at = timezone.now()
        if errors:
            raise ValidationError(errors)

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


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
    unit_measure = models.CharField(max_length=50)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
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
            new_stock = product.stock + self.get_stock_delta()

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

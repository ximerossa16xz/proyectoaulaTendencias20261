from django.db import models
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
        # Validate quantity > 0
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        # Get old status if this is an update
        old_status = None
        if self.pk:
            old_status = RestockOrder.objects.get(pk=self.pk).status

        # Increment stock if status changed to received
        if self.status == 'received' and old_status != 'received':
            self.product.stock += self.quantity
            self.product.save()
            self.received_at = timezone.now()

        super().save(*args, **kwargs)
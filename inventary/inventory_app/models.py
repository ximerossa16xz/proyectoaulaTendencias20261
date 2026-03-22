from django.db import models


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
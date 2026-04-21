from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, InventoryMovement, Product, RestockOrder, Supplier


class InventoryAPITestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='admin',
            password='testpass123',
            role='admin',
        )
        self.client.force_authenticate(self.user)

        self.category = Category.objects.create(
            name='Electronics',
            description='Devices and accessories',
            status='active',
        )
        self.supplier = Supplier.objects.create(
            name='Tech Supplier',
            nit='900123456',
            contact='Jane Doe',
            email='jane@example.com',
            phone='3001234567',
        )
        self.product = Product.objects.create(
            name='Keyboard',
            sku='KEY-001',
            category=self.category,
            supplier=self.supplier,
            unit_measure='unit',
            cost_price=Decimal('25.00'),
            sale_price=Decimal('40.00'),
            stock=10,
            minimum_stock=4,
        )

    def test_product_can_be_created_from_api(self):
        payload = {
            'name': 'Mouse',
            'sku': 'MSE-001',
            'category': self.category.id,
            'supplier': self.supplier.id,
            'unit_measure': 'unit',
            'cost_price': '15.00',
            'sale_price': '25.00',
            'stock': 8,
            'minimum_stock': 3,
        }

        response = self.client.post('/api/inventory/products/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.filter(sku='MSE-001').count(), 1)

    def test_inventory_movement_updates_stock(self):
        response = self.client.post('/api/inventory/movements/', {
            'product': self.product.id,
            'movement_type': InventoryMovement.MOVEMENT_TYPE_PURCHASE,
            'quantity': 5,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 15)
        self.assertEqual(InventoryMovement.objects.count(), 1)

    def test_inventory_movement_prevents_negative_stock(self):
        response = self.client.post('/api/inventory/movements/', {
            'product': self.product.id,
            'movement_type': InventoryMovement.MOVEMENT_TYPE_SALE,
            'quantity': 50,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(InventoryMovement.objects.count(), 0)

    def test_restock_order_received_updates_stock_only_once(self):
        create_response = self.client.post('/api/inventory/restock-orders/', {
            'supplier': self.supplier.id,
            'product': self.product.id,
            'quantity': 7,
            'status': 'pending',
        }, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        order_id = create_response.data['id']

        receive_response = self.client.patch(
            f'/api/inventory/restock-orders/{order_id}/',
            {'status': 'received'},
            format='json'
        )

        self.assertEqual(receive_response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 17)

        second_receive_response = self.client.patch(
            f'/api/inventory/restock-orders/{order_id}/',
            {'status': 'received'},
            format='json'
        )

        self.assertEqual(second_receive_response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 17)

        order = RestockOrder.objects.get(pk=order_id)
        self.assertIsNotNone(order.received_at)

    def test_low_stock_alert_endpoint_returns_only_products_below_minimum(self):
        Product.objects.create(
            name='Monitor',
            sku='MON-001',
            category=self.category,
            supplier=self.supplier,
            unit_measure='unit',
            cost_price=Decimal('100.00'),
            sale_price=Decimal('140.00'),
            stock=2,
            minimum_stock=5,
        )

        response = self.client.get('/api/inventory/products/alerts/low-stock/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [product['name'] for product in response.data]
        self.assertEqual(names, ['Monitor'])


class RestockOrderModelTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='operator',
            password='testpass123',
            role='admin',
        )
        self.category = Category.objects.create(
            name='Office',
            description='Office products',
            status='active',
        )
        self.supplier = Supplier.objects.create(
            name='Office Hub',
            nit='900654321',
            contact='John Doe',
            email='john@example.com',
            phone='3017654321',
        )
        self.product = Product.objects.create(
            name='Notebook',
            sku='NTB-001',
            category=self.category,
            supplier=self.supplier,
            unit_measure='unit',
            cost_price=Decimal('5.00'),
            sale_price=Decimal('9.00'),
            stock=6,
            minimum_stock=2,
        )

    def test_restock_order_requires_positive_quantity(self):
        order = RestockOrder(
            supplier=self.supplier,
            product=self.product,
            quantity=0,
            status='pending',
            created_by=self.user,
        )

        with self.assertRaises(ValidationError):
            order.save()

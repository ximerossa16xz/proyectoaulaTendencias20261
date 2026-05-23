from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models, transaction
from django.db.models import Sum, Count, F, DecimalField
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, InventoryMovement, Product, RestockOrder, Supplier, Warehouse, ProductWarehouseStock
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    InventoryMovementSerializer,
    ProductSerializer,
    RestockOrderSerializer,
    SupplierSerializer,
    BulkInventoryAdjustmentSerializer,
    WarehouseSerializer,
    ProductWarehouseStockSerializer,
)


@login_required
def dashboard_view(request):
    return render(request, 'inventory_app/index.html')


@login_required
def inventory_view(request):
    return render(request, 'inventory_app/inventory.html')


@login_required
def movements_view(request):
    return render(request, 'inventory_app/movements.html')


@login_required
def restock_view(request):
    return render(request, 'inventory_app/restock.html')


@login_required
def products_view(request):
    return render(request, 'inventory_app/products.html')


@login_required
def categories_view(request):
    return render(request, 'inventory_app/categories.html')


@login_required
def suppliers_view(request):
    return render(request, 'inventory_app/suppliers.html')


@login_required
def alerts_view(request):
    return render(request, 'inventory_app/alerts.html')


@login_required
def reports_view(request):
    return render(request, 'inventory_app/reports.html')


@login_required
def bulk_adjustment_view(request):
    return render(request, 'inventory_app/bulk_adjustment.html')


@login_required
def warehouses_view(request):
    return render(request, 'inventory_app/warehouses.html')


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Category.objects.annotate(product_count=models.Count('product')).order_by('name')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return Category.objects.annotate(product_count=models.Count('product')).order_by('name')


class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.order_by('name')
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.order_by('name')
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class WarehouseListCreateView(generics.ListCreateAPIView):
    queryset = Warehouse.objects.order_by('name')
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class WarehouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.order_by('name')
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class ProductWarehouseStockListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductWarehouseStockSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return ProductWarehouseStock.objects.select_related('product', 'warehouse').order_by('warehouse__name', 'product__name')

    def perform_create(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)


class ProductWarehouseStockDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductWarehouseStockSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return ProductWarehouseStock.objects.select_related('product', 'warehouse').order_by('warehouse__name', 'product__name')


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return Product.objects.select_related('category', 'supplier', 'primary_warehouse').prefetch_related('warehouse_stocks').order_by('name')


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category', 'supplier', 'primary_warehouse').prefetch_related('warehouse_stocks').order_by('name')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class InventoryMovementListCreateView(generics.ListCreateAPIView):
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return InventoryMovement.objects.select_related('product', 'user', 'warehouse').order_by('-timestamp')

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)


class InventoryMovementDetailView(generics.RetrieveAPIView):
    queryset = InventoryMovement.objects.select_related('product', 'user').order_by('-timestamp')
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


class RestockOrderListCreateView(generics.ListCreateAPIView):
    serializer_class = RestockOrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return RestockOrder.objects.select_related('supplier', 'product', 'created_by').order_by('-created_at')

    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)


class RestockOrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = RestockOrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return RestockOrder.objects.select_related('supplier', 'product', 'created_by').order_by('-created_at')

    def perform_update(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)


class LowStockAlertView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return Product.objects.select_related('category', 'supplier').filter(
            stock__lt=models.F('minimum_stock')
        ).order_by('stock', 'name')


class UpdateProductStockView(generics.UpdateAPIView):
    queryset = Product.objects.select_related('category', 'supplier').all()
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
        except DjangoValidationError as exc:
            return Response(
                exc.message_dict if hasattr(exc, 'message_dict') else {'detail': exc.messages},
                status=status.HTTP_400_BAD_REQUEST
            )


# Vistas de API para Reportes

class InventoryValorizationReportView(generics.ListAPIView):
    """
    Retorna la valorización total del inventario.
    Calcula: stock × precio de costo para cada producto
    """
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        
        total_inventory_value = 0
        product_valuations = []
        
        for product in products:
            valuation = product.stock * product.cost_price
            total_inventory_value += valuation
            product_valuations.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'stock': product.stock,
                'cost_price': float(product.cost_price),
                'valuation': float(valuation)
            })
        
        # Ordenar por valuación descendente
        product_valuations.sort(key=lambda x: x['valuation'], reverse=True)
        
        return Response({
            'total_inventory_value': float(total_inventory_value),
            'products': product_valuations,
            'product_count': len(product_valuations),
            'generated_at': timezone.now()
        })


class MovementsPeriodReportView(generics.ListAPIView):
    """
    Retorna los movimientos agrupados por período.
    Parámetros opcionales: start_date, end_date (YYYY-MM-DD)
    """
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        # Parámetros de filtro
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Valores por defecto: últimos 30 días
        if not end_date:
            end_date = timezone.now().date()
        else:
            try:
                from datetime import datetime
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except:
                return Response(
                    {'detail': 'Formato de end_date inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            try:
                from datetime import datetime
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except:
                return Response(
                    {'detail': 'Formato de start_date inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Filtrar movimientos
        movements = InventoryMovement.objects.filter(
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        ).select_related('product', 'user').order_by('timestamp')
        
        # Agrupar por tipo de movimiento
        movement_summary = {
            'purchase': {'count': 0, 'total_quantity': 0},
            'return': {'count': 0, 'total_quantity': 0},
            'sale': {'count': 0, 'total_quantity': 0},
            'adjustment': {'count': 0, 'total_quantity': 0},
            'disposal': {'count': 0, 'total_quantity': 0},
        }
        
        movements_list = []
        
        for movement in movements:
            movement_summary[movement.movement_type]['count'] += 1
            movement_summary[movement.movement_type]['total_quantity'] += movement.quantity
            
            movements_list.append({
                'id': movement.id,
                'product_name': movement.product.name,
                'movement_type': movement.movement_type,
                'quantity': movement.quantity,
                'user': movement.user.username if movement.user else 'N/A',
                'timestamp': movement.timestamp
            })
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'movement_summary': movement_summary,
            'total_movements': len(movements_list),
            'movements': movements_list,
            'generated_at': timezone.now()
        })


class ProductRotationRankingView(generics.ListAPIView):
    """
    Retorna ranking de productos con mayor rotación.
    Ordena por cantidad total de movimientos.
    Parámetro opcional: limit (default: 10)
    """
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        limit = int(request.query_params.get('limit', 10))
        
        # Obtener productos con anotación de movimientos
        products = Product.objects.annotate(
            movement_count=Count('inventory_movements'),
            total_quantity_moved=Sum('inventory_movements__quantity')
        ).order_by('-movement_count')[:limit]
        
        ranking = []
        for idx, product in enumerate(products, 1):
            ranking.append({
                'rank': idx,
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'category': product.category.name,
                'current_stock': product.stock,
                'movement_count': product.movement_count or 0,
                'total_quantity_moved': product.total_quantity_moved or 0,
                'rotation_percentage': (
                    ((product.total_quantity_moved or 0) / product.stock * 100)
                    if product.stock > 0 else 0
                )
            })
        
        return Response({
            'top_products': ranking,
            'total_products_analyzed': Product.objects.count(),
            'generated_at': timezone.now()
        })


class BulkInventoryAdjustmentView(generics.GenericAPIView):
    """
    Permite ajuste masivo de stock de productos.
    Registra movimientos de ajuste para auditoría.
    """
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def post(self, request, *args, **kwargs):
        serializer = BulkInventoryAdjustmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        adjustments = serializer.validated_data['adjustments']
        reason = serializer.validated_data['reason']
        user = request.user
        
        adjustment_results = []
        errors = []

        try:
            with transaction.atomic():
                for adjustment in adjustments:
                    try:
                        product = Product.objects.select_for_update().get(id=adjustment['product_id'])
                        old_stock = product.stock
                        new_stock = adjustment['new_stock']
                        
                        # Calcular delta
                        delta = new_stock - old_stock
                        
                        # Si no hay cambio, omitir
                        if delta == 0:
                            adjustment_results.append({
                                'product_id': product.id,
                                'product_name': product.name,
                                'old_stock': old_stock,
                                'new_stock': new_stock,
                                'delta': 0,
                                'status': 'skipped'
                            })
                            continue
                        
                        # Crear movimiento apropiado según el delta
                        # Para aumentos: usar 'return' (entra en INBOUND_TYPES)
                        # Para disminuciones: usar 'adjustment' (entra en OUTBOUND_TYPES)
                        if delta > 0:
                            # Aumento de stock: crear movimiento de 'return'
                            movement = InventoryMovement(
                                product=product,
                                movement_type=InventoryMovement.MOVEMENT_TYPE_RETURN,
                                quantity=delta,
                                user=user
                            )
                        else:
                            # Disminución de stock: crear movimiento de 'adjustment'
                            movement = InventoryMovement(
                                product=product,
                                movement_type=InventoryMovement.MOVEMENT_TYPE_ADJUSTMENT,
                                quantity=abs(delta),
                                user=user
                            )
                        
                        # Guardar movimiento (esto actualizará automáticamente el stock)
                        movement.save()
                        
                        # Refrescar producto para obtener el stock actualizado
                        product.refresh_from_db()
                        
                        adjustment_results.append({
                            'product_id': product.id,
                            'product_name': product.name,
                            'old_stock': old_stock,
                            'new_stock': product.stock,
                            'delta': delta,
                            'status': 'success'
                        })
                        
                    except Product.DoesNotExist:
                        errors.append({
                            'product_id': adjustment['product_id'],
                            'error': 'Producto no encontrado'
                        })
                    except DjangoValidationError as e:
                        errors.append({
                            'product_id': adjustment['product_id'],
                            'error': str(e.messages[0]) if hasattr(e, 'messages') else str(e)
                        })
                    except Exception as e:
                        errors.append({
                            'product_id': adjustment['product_id'],
                            'error': str(e)
                        })
            
            return Response({
                'status': 'success' if not errors else 'partial',
                'reason': reason,
                'total_adjustments': len(adjustments),
                'successful': len([r for r in adjustment_results if r['status'] == 'success']),
                'skipped': len([r for r in adjustment_results if r['status'] == 'skipped']),
                'failed': len(errors),
                'results': adjustment_results,
                'errors': errors,
                'processed_by': user.username,
                'processed_at': timezone.now()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

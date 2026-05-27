from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, logout, login as auth_login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import RegistrationForm
from .models import User

class UserProfileView(generics.RetrieveUpdateAPIView):
   
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.is_staff = user.role == 'admin'
            user.save()
            auth_login(request, user)

            next_url = request.POST.get('next') or reverse('dashboard')
            if not url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                next_url = reverse('dashboard')
            return redirect(next_url)
    else:
        form = RegistrationForm()

    return render(request, 'inventory_app/register.html', {'form': form})

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):

    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Proporciona username y password'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_staff': user.is_staff,
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def logout_view(request):

    logout(request)
    return HttpResponseRedirect(reverse('rest_framework:login'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
   
    user = request.user
    endpoints = {
        'usuario': {
            'perfil': '/api/accounts/profile/',
            'username': user.username,
            'email': user.email,
            'rol': user.role,
            'es_staff': user.is_staff,
        },
        'endpoints_disponibles': {
            'categorias': {
                'listar': '/api/inventory/categories/',
                'permiso': 'lectura' if user.role == 'operador' else 'lectura y escritura',
            },
            'proveedores': {
                'listar': '/api/inventory/suppliers/',
                'permiso': 'lectura' if user.role == 'operador' else 'lectura y escritura',
            },
            'productos': {
                'listar': '/api/inventory/products/',
                'permiso': 'lectura' if user.role == 'operador' else 'lectura y escritura',
            },
            'movimientos': {
                'listar': '/api/inventory/movements/',
                'permiso': 'lectura' if user.role == 'operador' else 'lectura y escritura',
            },
            'ordenes_reposicion': {
                'listar': '/api/inventory/restock-orders/',
                'permiso': 'lectura' if user.role == 'operador' else 'lectura y escritura',
            },
            'alertas_stock_bajo': {
                'listar': '/api/inventory/products/alerts/low-stock/',
                'permiso': 'lectura',
            },
        },
        'vistas_disponibles': {
            'dashboard': '/',
            'productos': '/inventory/products/',
            'categorias': '/inventory/categories/',
            'proveedores': '/inventory/suppliers/',
            'movimientos': '/inventory/movements/',
            'reposicion': '/inventory/restock/',
            'alertas': '/inventory/alerts/',
        },
        'permisos': {
            'puede_crear': user.role == 'admin',
            'puede_actualizar': user.role == 'admin',
            'puede_eliminar': user.role == 'admin',
            'puede_leer': True,
        }
    }

    return Response(endpoints, status=status.HTTP_200_OK)

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import User

class UserProfileView(generics.RetrieveUpdateAPIView):
   
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint que devuelve un token.
    Body: {"username": "usuario", "password": "contraseña"}
    """
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
    """
    Logout endpoint que cierra la sesión y redirecciona al login
    """
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
                'listar': '/api/categories/',
                'permiso': 'lectura' if user.role == 'operador' else 'lectura y escritura',
            },
            'proveedores': {
                'listar': '/api/suppliers/',
                'permiso': 'lectura' if user.role == 'operador' else 'lectura y escritura',
            },
            'productos': {
                'listar': '/api/products/',
                'permiso': 'lectura' if user.role == 'operador' else 'lectura y escritura',
            },
        },
        'permisos': {
            'puede_crear': user.role == 'admin',
            'puede_actualizar': user.role == 'admin',
            'puede_eliminar': user.role == 'admin',
            'puede_leer': True,
        }
    }

    return Response(endpoints, status=status.HTTP_200_OK)

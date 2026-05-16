from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('inventory_app.urls')),
    path('login/', auth_views.LoginView.as_view(
        template_name='inventory_app/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),

    path('api-auth/', include('rest_framework.urls')),

    path('api/inventory/', include('inventory_app.api_urls')),
    path('api/accounts/', include('accounts.urls')),
]
from django.contrib import admin
from django.urls import path, include
from accounts.views import logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('inventory_app.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api-auth/logout/', logout_view, name='api-logout'),
    path('api-auth/', include('rest_framework.urls')),
]

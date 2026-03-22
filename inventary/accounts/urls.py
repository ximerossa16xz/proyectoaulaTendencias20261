from django.urls import path
from .views import UserProfileView, dashboard_view, login_view, logout_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('dashboard/', dashboard_view, name='dashboard'),
]

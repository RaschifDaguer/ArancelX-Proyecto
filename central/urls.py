from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('limpiar-historial/', views.limpiar_historial, name='limpiar_historial'),
    path('gestionar-usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('gestionar-roles/', views.gestionar_roles, name='gestionar_roles'),
    path('admin-simplificado/', views.panel_admin_simplificado, name='panel_admin_simplificado'),
    path('admin-redirect/', views.admin_redirect, name='admin_redirect'),
]
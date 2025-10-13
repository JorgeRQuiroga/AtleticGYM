from django.urls import path
from . import views

urlpatterns = [
    path('clientes/menu/', views.cliente_menu, name='cliente_menu'),
    path('', views.cliente_listar, name='cliente_listar'),
    path('agregar/', views.cliente_agregar, name='cliente_agregar'),
    path('editar/<int:pk>/', views.cliente_editar, name='cliente_editar'),
    path('eliminar/<int:pk>/', views.cliente_eliminar, name='cliente_eliminar'),
]
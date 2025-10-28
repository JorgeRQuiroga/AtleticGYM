# empleados/urls.py
from django.urls import path
from . import views

app_name = 'empleados'

urlpatterns = [
    path('', views.empleado_menu, name='empleado_menu'),
    path('lista/', views.empleado_lista, name='empleado_lista'),
    path('agregar/', views.empleado_agregar, name='empleado_agregar'),
    path('editar/<int:pk>/', views.empleado_editar, name='empleado_editar'),
    path('eliminar/<int:pk>/', views.empleado_eliminar, name='empleado_eliminar'),
]
from django.urls import path
from . import views

app_name = 'servicios'

urlpatterns = [
    path('listar/',  views.servicio_listar, name='servicio_listar'),
    path('agregar/', views.servicio_agregar, name='servicio_agregar'),
    path('editar/<int:pk>/',   views.servicio_editar, name='servicio_editar'),
    path('eliminar/<int:pk>/', views.servicio_eliminar, name='servicio_eliminar'),
]
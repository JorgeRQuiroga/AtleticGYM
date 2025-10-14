from django.urls import path
from . import views

urlpatterns = [
    path('', views.usuario_listar, name='usuario_listar'),
    path('agregar/', views.usuario_agregar, name='usuario_agregar'),
    path('editar/<int:pk>/', views.usuario_editar, name='usuario_editar'),
    path('eliminar/<int:pk>/', views.usuario_eliminar, name='usuario_eliminar'),
    path('usuarios/menu/', views.usuario_menu, name='usuario_menu'),

]
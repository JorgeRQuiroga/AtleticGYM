from django.urls import path
from . import views

app_name = 'membresias'

urlpatterns = [
    path('inscribir/', views.inscribir_cliente, name='membresias_inscribir'),
    path('lista/', views.lista_membresias, name='membresias_lista'),
    path('', views.menu, name='membresias_menu'),
    path('borrar/<int:membresia_id>/', views.borrar_membresia, name='membresia_borrar'),
    path('detalle/<int:pk>/', views.membresias_detalle, name='membresias_detalle'),
    path('editar/<int:pk>/', views.membresias_editar, name='membresias_editar'),
    path('editar-partial/<int:pk>/', views.membresia_editar_partial, name='membresia_editar_partial'),
]
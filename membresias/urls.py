from django.urls import path
from . import views

app_name = 'membresias'

urlpatterns = [
    path('inscribir/', views.inscribir_cliente, name='membresias_inscribir'),
    path('lista/', views.lista_membresias, name='membresias_lista'),
    path('', views.menu, name='membresias_menu'),
    path('grafico_membresias/', views.grafico_membresias, name='grafico_membresias'),
    path('borrar/<int:membresia_id>/', views.borrar_membresia, name='membresia_borrar'),
    path('buscar/', views.buscar_membresia_por_dni, name='membresias_buscar'),
    
]
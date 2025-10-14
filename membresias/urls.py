from django.urls import path
from . import views

app_name = 'membresias'

urlpatterns = [
    path('inscribir/', views.inscribir_cliente, name='membresias_inscribir'),
    path('lista/', views.lista_membresias, name='membresias_lista'),
    path('', views.menu, name='membresias_menu'),
]
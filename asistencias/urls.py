from django.urls import path
from . import views

app_name = 'asistencias'

urlpatterns = [
    # 1. La URL para el menú de opciones
    path('opciones/', views.asistencia_opciones, name='asistencia_opciones'),
    # 2. La URL para la pantalla de registro del cliente (modo kiosco)
    path('registrar/', views.registrar_asistencia, name='asistencia_registrar'),
    # 3. La URL para que el admin vea el historial de asistencias
    path('lista/', views.lista_asistencias, name='asistencia_lista'),
]
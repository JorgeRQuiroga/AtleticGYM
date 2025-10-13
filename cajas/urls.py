from django.urls import path
from . import views

urlpatterns = [
    path('abrir/', views.abrir_caja, name='caja_abrir'),
    path('cerrar/', views.cerrar_caja, name='caja_cerrar'),
    path('estado/', views.estado_caja, name='caja_estado'),
]

from django.urls import path
from . import views

app_name = 'cajas'

urlpatterns = [
    path('abrir/', views.abrir_caja, name='caja_abrir'),
    path('cerrar/', views.cerrar_caja, name='caja_cerrar'),
    path('estado/', views.estado_caja, name='caja_estado'),
    path('arqueo/', views.caja_arqueo, name='caja_arqueo'),
    path('grafico_caja/', views.grafico_caja, name='grafico_caja'),
]

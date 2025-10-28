from django.urls import path
from . import views

app_name = 'cobros'

urlpatterns = [
    path('nuevo/', views.nuevo_cobro, name='cobros_nuevo'),
    path('lista/', views.lista_cobros, name='cobros_lista'),
    path('detalle/<int:pk>/', views.detalle_cobro, name='cobros_detalle'),
    path('informe/',views.cobros_informe, name='cobros_informe'),
]
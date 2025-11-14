from django.urls import path
from . import views

urlpatterns = [
    path('nuevo/', views.nuevo_cobro, name='cobros_nuevo'),
    path('lista/', views.lista_cobros, name='cobros_lista'),
    path('detalle/<int:pk>/', views.detalle_cobro, name='cobros_detalle'),
    path('buscar-dni/', views.buscar_dni, name='buscar_dni'),
    path('un-dia/', views.cobro_un_dia, name='cobros_un_dia'),
    path('extraccion/', views.extraccion_cobros, name='cobros_extraccion'),
    path('extracciones/lista', views.mostrar_extracciones, name='cobros_mostrar_extracciones'),
    path('extracciones/lista/detalle/<int:pk>', views.extraccion_detalle, name='extraccion_detalle')
]
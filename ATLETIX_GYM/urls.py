from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from ATLETIX_GYM import views
from django.conf.urls import handler403

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', include('login.urls')),
    path('caja/', include('cajas.urls')),
    path('clientes/', include('clientes.urls')),
    path('servicios/', include('servicios.urls')),
    path('cobros/', include('cobros.urls')),
    path('membresias/', include('membresias.urls')),
    path('asistencias/', include('asistencias.urls')),
    path('empleados/', include('empleados.urls')),
    path('graficos/', include('graficos.urls')),
    path('terminos-y-condiciones/', views.terminos_condiciones, name='terminos_condiciones'),
]

handler403 = 'login.views.error_403'
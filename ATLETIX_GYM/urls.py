from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),
    path('usuarios/', include('usuarios.urls')),
    path('clientes/', include('clientes.urls')),
]
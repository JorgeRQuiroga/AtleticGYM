from django.urls import path
from . import views

app_name = "graficos"

urlpatterns = [
    path("", views.menu_graficos, name="graficos_menu"),
    path("graficos-asistencias/", views.grafico_asistencias, name="graficos_asistencias"),
    path("graficos-asistencias/datos/", views.datos_asistencias, name="datos_asistencias"),
]

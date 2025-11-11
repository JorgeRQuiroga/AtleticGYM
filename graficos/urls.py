from django.urls import path
from . import views

app_name = "graficos"

urlpatterns = [
    path("", views.menu_graficos, name="graficos_menu"),
    path("graficos-asistencias/", views.grafico_asistencias, name="graficos_asistencia"),
    path("graficos-membresias/", views.grafico_membresias, name="graficos_membresias"),
    path("graficos-ingresos/", views.grafico_ingresos, name="graficos_ingresos"),
]    
from django.urls import path
from . import views

app_name = 'asistencias'

urlpatterns = [
    path('registrar/', views.registrar_asistencia, name='asistencia_opciones'),
    #path('asistencias/', views.asistencia_form, name='asistencia_listar'),
]
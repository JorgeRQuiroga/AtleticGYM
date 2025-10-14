from django.urls import path
from . import views

app_name = 'asistencias'

urlpatterns = [
    path('registrar/', views.asistencia_guardar, name='registrar_asistencia'),
    path('asistencias/', views.asistencia_form, name='asistencia_listar'),
]
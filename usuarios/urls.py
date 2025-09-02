from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('asistencia/registrar/', views.registrar_asistencia, name='registrar_asistencia'),
    path('asistencias/', views.asistencia_listar, name='asistencia_listar'),
    path('', views.usuario_listar, name='usuario_listar'),
    path('agregar/', views.usuario_agregar, name='usuario_agregar'),
    path('editar/<int:pk>/', views.usuario_editar, name='usuario_editar'),
    path('eliminar/<int:pk>/', views.usuario_eliminar, name='usuario_eliminar'),
]
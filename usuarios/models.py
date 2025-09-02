from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from ATLETIX_GYM import settings

class Usuario(AbstractUser):
    dni = models.IntegerField(null=True, blank=True, verbose_name="DNI")
    telefono = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.username
    
class Asistencia(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
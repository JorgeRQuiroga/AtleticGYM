from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    domicilio = models.CharField(max_length=200, blank=True, null=True)
    fecha_baja = models.DateField(blank=True, null=True)
    fecha_hora_alta = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def dar_baja(self):
        self.activo = False
        self.fecha_baja = timezone.now()
        self.save()

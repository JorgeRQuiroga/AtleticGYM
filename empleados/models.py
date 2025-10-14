from django.db import models

class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    domicilio = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    puesto = models.CharField(max_length=100, blank=True, null=True)
    fecha_contratacion = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.puesto if self.puesto else 'Sin puesto'}"
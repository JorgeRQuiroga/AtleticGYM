# clientes/models.py
from django.db import models

class Cliente(models.Model):
    dni = models.IntegerField("DNI")
    nombre = models.CharField("Nombre", max_length=30)
    apellido = models.CharField("Apellido", max_length=30)
    email = models.EmailField("Email", null=True, blank=True)
    telefono = models.CharField("Teléfono", max_length=20, null=True, blank=True)
    emergencia = models.CharField("Emergencia", max_length=20, blank=True, null=True)
    domicilio = models.CharField("Domicilio", max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} (DNI: {self.dni})"
    

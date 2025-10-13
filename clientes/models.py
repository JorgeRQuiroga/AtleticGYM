# clientes/models.py
from django.db import models
from servicios.models import Servicio

class Cliente(models.Model):
    dni = models.IntegerField("DNI", unique=True)
    nombre = models.CharField("Nombre", max_length=30)
    apellido = models.CharField("Apellido", max_length=30)
    email = models.EmailField("Email", unique=True, blank=True, null=True)
    telefono = models.CharField("Teléfono", max_length=20)
    emergencia = models.CharField("Emergencia", max_length=20, blank=True)

    # Nuevo: servicio asignado y estado de membresía
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Servicio")
    membresia_activa = models.BooleanField("Membresía activa", default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.dni})"

class AsistenciaCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente.nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

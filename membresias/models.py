from django.db import models
from clientes.models import Cliente
from servicios.models import Servicio

class Membresia(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='membresia')
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField()
    clases_restantes = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, default='Ninguna')

    def __str__(self):
        return f"Membresía de {self.cliente.nombre} {self.cliente.apellido}"

    def borrar(self):
        self.activa = False
        self.save()
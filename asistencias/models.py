from django.utils import timezone
from membresias.models import Membresia
from django.db import models

class Asistencia(models.Model):
    # La asistencia siempre está ligada a una membresía de un cliente
    membresia = models.ForeignKey(Membresia, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_hora = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.membresia and self.membresia.cliente:
            return f"Asistencia de {self.membresia.cliente} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
        return f"Asistencia registrada el {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

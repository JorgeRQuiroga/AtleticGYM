from django.utils import timezone
from django.contrib.auth import get_user_model
from clientes.models import Cliente
from empleados.models import Empleado
from membresias.models import Membresia
from django.db import models

class Asistencia(models.Model):
    TIPO_CHOICES = [
        ('cliente', 'Cliente'),
        ('empleado', 'Empleado'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    empleado = models.ForeignKey(Empleado, null=True, blank=True, on_delete=models.CASCADE)
    membresia = models.ForeignKey(Membresia, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_hora = models.DateTimeField(default=timezone.now)
    registrado_por = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)

    def __str__(self):
        if self.tipo == 'cliente' and self.cliente:
            return f"Asistencia cliente {self.cliente.nombre} - {self.fecha_hora}"
        elif self.tipo == 'empleado' and self.empleado:
            return f"Asistencia empleado {self.empleado.nombre} - {self.fecha_hora}"
        return f"Asistencia {self.fecha_hora}"
    

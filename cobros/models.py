from django.db import models
from django.conf import settings
from servicios.models import Servicio
from cajas.models import Caja
from django.utils import timezone
from clientes.models import Cliente

User = settings.AUTH_USER_MODEL

class Cobro(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT, related_name='cobros')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cobros')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    servicio = models.ForeignKey('servicios.Servicio', on_delete=models.PROTECT)

    class Meta:
        ordering = ['-fecha_hora']
    
    def save(self, *args, **kwargs):
        if self.servicio and (not self.total or self.total == 0):
            self.total = self.servicio.precio
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cobro {self.id} ${self.total} por {self.servicio.nombre} en caja {self.caja.id} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"
    
class MetodoDePago(models.Model):
    metodoDePago = models.CharField(max_length=100)

    def __str__(self):
        return self.metodoDePago
    
class DetalleCobro(models.Model):
    servicio = models.ForeignKey('servicios.Servicio', on_delete=models.PROTECT, related_name='detalles_cobro')
    cobro = models.ForeignKey(Cobro, on_delete=models.PROTECT, related_name='detalles_cobro')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodoDePago = models.ForeignKey(MetodoDePago, on_delete=models.PROTECT, related_name='detalles_cobro')
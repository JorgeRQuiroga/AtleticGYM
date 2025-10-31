from django.db import models
from django.contrib.auth.models import User

class Caja(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    monto_apertura = models.DecimalField(max_digits=10, decimal_places=2)
    monto_cierre = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=10, choices=[('abierta', 'Abierta'), ('cerrada', 'Cerrada')], default='abierta')
    total_en_caja = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Caja de {self.usuario.username} - {self.estado}"

    def registrar_ingreso(self, monto):
        self.total_en_caja += monto
        self.save()

    def registrar_egreso(self, monto):
        self.total_en_caja -= monto
        self.save()
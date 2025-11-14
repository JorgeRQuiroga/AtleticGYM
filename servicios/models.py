from django.db import models

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    dias_semana = models.IntegerField(default=3)
    cantidad_clases = models.IntegerField()
    dias_semana = models.IntegerField(default=3)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

    def soft_delete(self):
        self.activo = False
        self.save()
from django.db import models
from django.core.validators import RegexValidator

class Servicio(models.Model):
    nombre   = models.CharField('Nombre', max_length=50)
    cantidad = models.CharField('Cantidad de Clases',max_length=10, default='0', validators=[RegexValidator(regex=r'^\d+$', message='Solo dígitos permitidos')])
    precio   = models.CharField('Precio', max_length=15, default='0.00', validators=[RegexValidator(regex=r'^\d+(\.\d{1,2})?$', message='Formato inválido: use solo números con hasta dos decimales')])
    ESTADOS  = [(True, 'Activo'), (False, 'Inactivo')]
    estado   = models.BooleanField('Estado', default=True, choices=ESTADOS)

    def __str__(self):
        return f"{self.nombre} [{self.get_estado_display()}]"
from django.contrib.auth.models import User
from django.db import models
from ATLETIX_GYM import settings

    
class Empleado(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
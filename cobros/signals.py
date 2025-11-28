from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from .models import Caja
import logging
logger = logging.getLogger(__name__)

@receiver(user_logged_out)
def cerrar_caja_al_logout(sender, request, user, **kwargs):
    print(f"Logout detectado para usuario {user}")
    cajas = Caja.objects.filter(usuario=user)
    print("Cajas encontradas:", list(cajas.values()))
    caja_abierta = cajas.filter(estado='abierta').last()
    if caja_abierta:
        caja_abierta.cerrar()
        print(f"Caja {caja_abierta.id} cerrada")
    else:
        print("No había caja abierta")

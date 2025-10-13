from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from apertura_y_cierre_de_caja.models import Caja

def caja_abierta_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        abierto = Caja.objects.filter(usuario=request.user, estado='abierta').first()
        if not abierto:
            messages.warning(request, "No hay una caja abierta. Debes abrirla antes de registrar cobros.")
            return redirect('estado_caja')
        request.caja_abierta = abierto
        return view_func(request, *args, **kwargs)
    return _wrapped

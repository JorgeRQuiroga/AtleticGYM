from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Caja , ConfiguracionCaja
from .forms import AperturaCajaForm, CierreCajaForm
from django.utils import timezone
from django.contrib import messages
from django.conf import settings

@login_required
def abrir_caja(request):
    if Caja.objects.filter(usuario=request.user, estado='abierta').exists():
        next_url = request.GET.get('next')
        return redirect(next_url or 'cobros_lista')

    # Usar el valor fijo en lugar de la última caja
    config = ConfiguracionCaja.objects.first()
    monto_inicial = config.monto_inicial if config else 0.0
    if request.method == 'POST':
        form = AperturaCajaForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.usuario = request.user
            caja.estado = 'abierta'
            caja.fecha_apertura = timezone.now()
            caja.total_en_caja = caja.monto_apertura
            caja.save()
            return redirect(request.POST.get('next') or 'cobros_lista')
    else:
        form = AperturaCajaForm(initial={'monto_apertura': monto_inicial})

    return render(request, 'caja_abrir.html', {
        'form': form,
        'usuario': request.user,
        'monto_sugerido': monto_inicial,
        'next': request.GET.get('next', '')
    })

@login_required
def cerrar_caja(request):
    caja = get_object_or_404(Caja, usuario=request.user, estado='abierta')

    if request.method == 'POST':
        # Aquí deberías calcular el total real de la caja (ventas, ingresos, etc.)
        # Para este ejemplo, usamos el mismo monto de apertura como placeholder
        # total_calculado = caja.total_en_caja 

        caja.monto_cierre = caja.total_en_caja
        caja.estado = 'cerrada'
        caja.fecha_cierre = timezone.now()
        caja.save()
        messages.success(request, "Caja cerrada correctamente.")
        return redirect('caja_estado')

    return render(request, 'caja_cerrar.html', {
        'usuario': request.user,
        'caja': caja
    })



@login_required
def estado_caja(request):
    caja = Caja.objects.filter(usuario=request.user).order_by('-fecha_apertura').first()
    return render(request, 'caja_estado.html', {'caja': caja})

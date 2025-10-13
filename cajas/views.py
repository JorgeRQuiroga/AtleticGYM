from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Caja
from .forms import AperturaCajaForm, CierreCajaForm
from django.utils import timezone
from django.contrib import messages

@login_required
def abrir_caja(request):
    if Caja.objects.filter(usuario=request.user, estado='abierta').exists():
        return redirect('caja_estado')

    ultima_caja = Caja.objects.filter(usuario=request.user, estado='cerrada').order_by('-fecha_cierre').first()
    monto_inicial = ultima_caja.monto_cierre if ultima_caja else 0

    if request.method == 'POST':
        form = AperturaCajaForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.usuario = request.user
            caja.estado = 'abierta'
            caja.fecha_apertura = timezone.now()
            caja.save()
            return redirect('caja_estado')
    else:
        form = AperturaCajaForm(initial={'monto_apertura': monto_inicial})

    return render(request, 'caja_abrir.html', {
        'form': form,
        'usuario': request.user,
        'monto_sugerido': monto_inicial
    })

@login_required
def cerrar_caja(request):
    caja = get_object_or_404(Caja, usuario=request.user, estado='abierta')

    if request.method == 'POST':
        # Aquí deberías calcular el total real de la caja (ventas, ingresos, etc.)
        # Para este ejemplo, usamos el mismo monto de apertura como placeholder
        total_calculado = caja.monto_apertura  # Reemplazar con lógica real

        caja.monto_cierre = total_calculado
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

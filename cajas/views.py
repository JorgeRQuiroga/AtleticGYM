from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Caja
from .forms import AperturaCajaForm, CierreCajaForm
from django.utils import timezone
from django.contrib import messages

@login_required
def abrir_caja(request):
    # Si la caja ya está abierta, no mostramos el modal de apertura.
    # En su lugar, redirigimos al usuario a donde iba o a la lista de cobros.
    if Caja.objects.filter(usuario=request.user, estado='abierta').exists():
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('cobros_lista') # Opción por defecto si no hay 'next'

    ultima_caja = Caja.objects.filter(usuario=request.user, estado='cerrada').order_by('-fecha_cierre').first()
    monto_inicial = ultima_caja.monto_cierre if ultima_caja else 0

    if request.method == 'POST':
        form = AperturaCajaForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.usuario = request.user
            caja.estado = 'abierta'
            caja.fecha_apertura = timezone.now()
            caja.total_en_caja = caja.monto_apertura

            caja.save()
            
            # Redirigir a la página siguiente si existe, o a la lista de cobros por defecto
            next_url = request.POST.get('next') # Lo tomamos del POST
            if next_url:
                return redirect(next_url)
            return redirect('cobros_lista')
    else:
        form = AperturaCajaForm(initial={'monto_apertura': monto_inicial})

    return render(request, 'caja_abrir.html', {
        'form': form,
        'usuario': request.user,
        'monto_sugerido': monto_inicial,
        'next': request.GET.get('next', '') # Pasar el 'next' a la plantilla
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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Caja
from cobros.models import Cobro
from .forms import AperturaCajaForm, CierreCajaForm
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay

@login_required
def abrir_caja(request):
    # Si la caja ya está abierta, no mostramos el modal de apertura.
    # En su lugar, redirigimos al usuario a donde iba o a la lista de cobros.
    if Caja.objects.filter(usuario=request.user, estado='abierta').exists():
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('cobros:cobros_lista') # Opción por defecto si no hay 'next'

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
            return redirect('cobros:cobros_lista')
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
        return redirect('cajas:caja_estado')

    return render(request, 'caja_cerrar.html', {
        'usuario': request.user,
        'caja': caja
    })



@login_required
def estado_caja(request):
    caja = Caja.objects.filter(usuario=request.user).order_by('-fecha_apertura').first()
    return render(request, 'caja_estado.html', {'caja': caja})

@login_required
def caja_arqueo(request):
    # Obtenemos todas las cajas con estado 'cerrada' y las pasamos a la plantilla
    arqueos = Caja.objects.filter(estado='cerrada').select_related('usuario').order_by('-fecha_cierre')
    context = {'arqueos': arqueos}
    return render(request, 'caja_arqueo.html', context)

@login_required
def grafico_caja(request):
    # Determinar el período a analizar
    periodo_str = request.GET.get('periodo', timezone.now().strftime('%Y-%m'))
    try:
        year, month = map(int, periodo_str.split('-'))
        periodo_dt = timezone.datetime(year, month, 1)
    except (ValueError, TypeError):
        periodo_dt = timezone.now()
        year, month = periodo_dt.year, periodo_dt.month

    # 1. Ingreso del Mes
    ingreso_mes = Cobro.objects.filter(
        fecha_hora__year=year,
        fecha_hora__month=month
    ).aggregate(total=Sum('total'))['total'] or 0

    # 2. Día con Más Ingreso
    mejor_dia_data = Cobro.objects.filter(
        fecha_hora__year=year,
        fecha_hora__month=month
    ).annotate(
        dia=TruncDay('fecha_hora')
    ).values('dia').annotate(
        ingreso_diario=Sum('total')
    ).order_by('-ingreso_diario').first()

    # 3. Usuario Más Activo (basado en cantidad de cobros)
    usuario_activo_data = Cobro.objects.filter(
        fecha_hora__year=year,
        fecha_hora__month=month
    ).values('caja__usuario__username').annotate(
        num_cobros=Count('id')
    ).order_by('-num_cobros').first()

    # 4. Diferencias en Arqueos (siempre será 0 por ahora)
    diferencia_total = 0.00

    context = {
        'periodo_actual': periodo_dt.strftime('%Y-%m'),
        'mes_actual_str': periodo_dt.strftime('%B de %Y').capitalize(),
        'ingreso_mes': ingreso_mes,
        'mejor_dia_data': mejor_dia_data,
        'usuario_activo_data': usuario_activo_data,
        'diferencia_total': diferencia_total,
    }
    return render(request, 'grafico_caja.html', context)
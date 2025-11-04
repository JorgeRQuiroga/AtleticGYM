from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cobro, MetodoDePago
from .forms import CobroForm
from .decorators import caja_abierta_required
from servicios.models import Servicio
from clientes.models import Cliente
from membresias.models import Membresia
from django.http import JsonResponse
from cajas.models import Caja

@login_required
@caja_abierta_required
def nuevo_cobro(request):
    caja = request.caja_abierta
    if request.method == 'POST':
        form = CobroForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni'].strip()
            membresia = Membresia.objects.select_related('cliente').filter(cliente__dni__iexact=dni, activa=True).first()

            if not membresia:
                messages.error(request, "No se encontró una membresía activa para ese DNI.")
                return render(request, 'cobro_nuevo.html', {'form': form})

            cobro = form.save(commit=False)
            cobro.caja = caja
            cobro.cliente = membresia.cliente
            cobro.membresia = membresia

            # Asumimos que el modelo Cobro tiene un campo 'total' y no 'importe'.
            # Si la membresía tiene un servicio asociado, usamos su precio.
            if membresia.servicio:
                cobro.total = membresia.servicio.precio
            else:
                # Manejar el caso donde no hay servicio o el precio se define de otra forma
                # Por ahora, lo dejamos en 0 y mostramos un error si es necesario.
                # O podrías tomarlo del formulario si hay un campo para el monto.
                messages.error(request, "La membresía no tiene un servicio con precio asociado.")
                return render(request, 'cobro_nuevo.html', {'form': form})

            cobro.save()

            if caja.total_en_caja is None:
                caja.total_en_caja = caja.monto_apertura
            caja.total_en_caja += cobro.total
            caja.save()
            messages.success(request, f"Cobro de ${cobro.total} registrado para {membresia.cliente}.")
            return redirect('cobros:cobros_lista')
    else:
        form = CobroForm()
    return render(request, 'cobro_nuevo.html', {'form': form, 'caja': caja})


@login_required
@caja_abierta_required
def lista_cobros(request):
    caja = request.caja_abierta
    cobros = Cobro.objects.filter(caja=caja).order_by('-fecha_hora')
    return render(request, 'cobros_lista.html', {'cobros': cobros, 'caja': caja})

@login_required
@caja_abierta_required
def detalle_cobro(request, pk):
    caja = request.caja_abierta
    cobro = get_object_or_404(Cobro, pk=pk, caja=caja)
    return render(request, 'cobros_detalle.html', {'cobro': cobro, 'caja': caja})

@login_required
def cobros_informe(request):
    cobros = Cobro.objects.select_related(
        'cliente', 'servicio', 'caja__usuario'
    ).all()
    context = {'cobros': cobros}
    return render(request, 'cobros_informe.html', context)

@login_required
def buscar_dni(request):
    q = request.GET.get('q', '')
    resultados = []
    if q:
        # Busca clientes que tengan una membresía activa, para sugerir solo DNI cobrables.
        clientes = Cliente.objects.filter(dni__icontains=q)[:10]
        resultados = [
            {"id": c.id, "dni": c.dni, "nombre": f"{c.apellido}, {c.nombre}"}
            for c in clientes
        ]
    return JsonResponse(resultados, safe=False)

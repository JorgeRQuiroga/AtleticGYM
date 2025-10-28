from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cobro
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
            cobro.caja = Caja.objects.get(estado='abierta', usuario=request.user)
            cobro.cliente = membresia.cliente
            cobro.membresia = membresia
            cobro.importe = membresia.servicio.precio  # si aplica
            cobro.save()

            messages.success(request, f"Cobro registrado para {membresia.cliente}.")
            return redirect('cobros_lista')
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
def buscar_dni(request):
    q = request.GET.get('q', '')
    resultados = []
    if q:
        clientes = Cliente.objects.filter(dni__icontains=q)[:10]
        resultados = [
            {"id": c.id, "dni": c.dni, "nombre": f"{c.apellido}, {c.nombre}"}
            for c in clientes
        ]
    return JsonResponse(resultados, safe=False)
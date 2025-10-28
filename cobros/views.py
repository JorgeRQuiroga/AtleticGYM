from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cobro, MetodoDePago
from .forms import CobroForm
from .decorators import caja_abierta_required
from servicios.models import Servicio
from clientes.models import Cliente

@login_required
@caja_abierta_required
def nuevo_cobro(request):
    caja = request.caja_abierta
    if request.method == 'POST':
        form = CobroForm(request.POST)
        if form.is_valid():
            cobro = form.save(commit=False)
            cobro.caja = caja
            cobro.cliente = form.cleaned_data['cliente'].cliente  # Asignar el cliente desde la membresía seleccionada
            
            # Usar el campo 'total' que sí existe en el modelo Cobro
            if cobro.servicio:
                cobro.total = cobro.servicio.precio
            
            cobro.save()

            if caja.total_en_caja is None:
                caja.total_en_caja = caja.monto_apertura
            caja.total_en_caja += cobro.total # Usar 'total' para actualizar el monto de la caja
            caja.save()
            messages.success(request, "Cobro registrado correctamente.")
            return redirect('cobros:cobros_lista') # Corregir la redirección para usar el namespace
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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cobro
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
            cobro.usuario = request.user
            cobro.caja = caja
            cobro.cliente = form.cleaned_data['cliente'].cliente  # Asignar el cliente desde la membresía seleccionada
            if cobro.servicio:
                cobro.importe = cobro.servicio.precio
            cobro.save()
            if caja.total_en_caja is None:
                caja.total_en_caja = caja.monto_apertura
            caja.total_en_caja = caja.total_en_caja + cobro.importe
            caja.save()
            messages.success(request, "Cobro registrado correctamente.")
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
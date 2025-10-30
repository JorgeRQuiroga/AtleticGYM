from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cobro, DetalleCobro, MetodoDePago
from .forms import CobroForm, CobroClaseForm, ExtraccionForm
from django.utils import timezone
from .decorators import caja_abierta_required
from servicios.models import Servicio
from clientes.models import Cliente
from membresias.models import Membresia
from django.http import JsonResponse
from cajas.models import Caja
from membresias.forms import MembresiaInscripcionForm

@login_required
@caja_abierta_required
def nuevo_cobro(request):
    caja = Caja.objects.filter(estado='abierta', usuario=request.user).first()
    if not caja:
        messages.error(request, "No hay una caja abierta para registrar el cobro.")
        return redirect('cobros_lista')

    if request.method == 'POST':
        form = CobroForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni'].strip()
            cliente = get_object_or_404(Cliente.objects.exclude(nombre="-----"), dni=dni)
            # Buscar membresía activa
            membresia = Membresia.objects.filter(cliente=cliente).select_related('servicio').first()

            if not membresia:
                messages.error(request, "El cliente no tiene ninguna membresía registrada.")
                return render(request, 'cobro_nuevo.html', {'form': form, 'caja': caja})

            # Si la membresía existe pero está inactiva, reactivarla
            if not membresia.activa:
                membresia.activa = True
                membresia.save()

            cobro = form.save(commit=False)
            cobro.caja = caja
            cobro.cliente = cliente

            # Si el usuario no cambió el servicio, usar el de la membresía
            servicio = form.cleaned_data.get('servicio') or membresia.servicio
            cobro.servicio = servicio
            cobro.total = servicio.precio
            cobro.save()
            if servicio != membresia.servicio:
                membresia.servicio = servicio
                membresia.save()
            metodo_pago = form.cleaned_data['metodo_pago']
            DetalleCobro.objects.create(
                cobro=cobro,
                servicio=servicio,
                monto=cobro.total,
                metodoDePago=metodo_pago
            )
            caja.total_en_caja += cobro.total
            caja.save()
            messages.success(request, f"Cobro registrado para {cliente}.")
            return redirect('cobros_lista')
    else:
        form = CobroForm()

    return render(request, 'cobro_nuevo.html', {'form': form, 'caja': caja})

@login_required
@caja_abierta_required
def cobro_un_dia(request):
    caja = Caja.objects.filter(estado='abierta', usuario=request.user).first()
    if not caja:
        messages.error(request, "No hay una caja abierta para registrar el cobro.")
        return redirect('cobros_lista')

    if request.method == 'POST':
        form = CobroClaseForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni'].strip()
            servicio = Servicio.objects.get(nombre="Por clase")
            metodo_pago = form.cleaned_data['metodo_pago']

            cliente = Cliente.objects.create(
                dni=dni,
                nombre="-----",
                apellido="",
                telefono="",
                email=""
            )
            # Crear el cobro
            cobro = Cobro.objects.create(
                caja=caja,
                cliente=cliente,
                servicio=servicio,
                total=servicio.precio,
                descripcion="Cobro por clase suelta",
                fecha_hora=timezone.now()
            )

            # Crear detalle
            DetalleCobro.objects.create(
                cobro=cobro,
                servicio=servicio,
                monto=servicio.precio,
                metodoDePago=metodo_pago
            )

            messages.success(request, f"Cobro por clase registrado (${servicio.precio}).")
            return redirect('cobros_lista')
    else:
        form = CobroClaseForm()

    return render(request, 'cobro_un_dia.html', {'form': form, 'caja': caja})   


@login_required
@caja_abierta_required
def lista_cobros(request):
    form = MembresiaInscripcionForm()
    caja = request.caja_abierta
    cobros = Cobro.objects.filter(caja=caja).order_by('-fecha_hora')
    return render(request, 'cobros_lista.html', {'cobros': cobros, 'caja': caja, 'form': form})

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

@login_required
@caja_abierta_required
def extraccion_cobros(request):
    caja = Caja.objects.filter(estado='abierta', usuario=request.user).first()
    if not caja:
        messages.error(request, "No hay una caja abierta para registrar la extracción.")
        return redirect('cobros_lista')

    if request.method == 'POST':
        form = ExtraccionForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data['monto']

            #Verificar saldo suficiente
            saldo_actual = getattr(caja, 'saldo_actual', getattr(caja, 'total_en_caja', 0))
            if monto > saldo_actual:
                messages.error(request, f"No hay fondos suficientes en la caja. Saldo disponible: ${saldo_actual}")
                return render(request, 'cobros_extraccion.html', {'form': form, 'caja': caja})

            #Registrar extracción
            extraccion = form.save(commit=False)
            extraccion.caja = caja
            extraccion.usuario = request.user
            extraccion.save()

            #Actualizar saldo
            if hasattr(caja, 'saldo_actual'):
                caja.saldo_actual -= extraccion.monto
            elif hasattr(caja, 'total_en_caja'):
                caja.total_en_caja -= extraccion.monto
            caja.save()

            messages.success(
                request,
                f"Extracción de ${extraccion.monto} registrada. Nuevo saldo: ${getattr(caja, 'saldo_actual', caja.total_en_caja)}"
            )
            return redirect('cobros_lista')
    else:
        form = ExtraccionForm()

    return render(request, 'cobros_extraccion.html', {'form': form, 'caja': caja})
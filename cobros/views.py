from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cobro, DetalleCobro, MetodoDePago, Extraccion
from .forms import CobroForm, CobroClaseForm, ExtraccionForm
from django.utils import timezone
from .decorators import caja_abierta_required
from servicios.models import Servicio
from clientes.models import Cliente
from membresias.models import Membresia
from django.http import JsonResponse
from cajas.models import Caja
from membresias.forms import MembresiaInscripcionForm
from django.db.models import Q
from django.core.paginator import Paginator

@login_required
@caja_abierta_required
def nuevo_cobro(request):
    caja = Caja.objects.filter(estado='abierta', usuario=request.user).first()
    if not caja:
        messages.error(request, "No hay una caja abierta para registrar el cobro.")
        return redirect('cobros_lista')

    # Queryset base: todos los servicios excepto el que se llame "Por Clase" (case-insensitive)
    servicios_base = Servicio.objects.exclude(nombre__iexact='Por Clase')

    if request.method == 'POST':
        # obtener dni crudo para poder conocer la membresía antes de validar el form
        raw_dni = request.POST.get('dni', '').strip()
        cliente = Cliente.objects.filter(dni=raw_dni).exclude(nombre="-----").first()
        membresia = None
        if cliente:
            membresia = Membresia.objects.filter(cliente=cliente).select_related('servicio').first()

        # si querés permitir usar la membresía aunque su servicio sea "Por Clase",
        # incluí ese servicio en el queryset
        servicios_qs = servicios_base
        if membresia and membresia.servicio:
            if membresia.servicio.nombre.lower() == 'por clase':
                servicios_qs = Servicio.objects.filter(pk=membresia.servicio.pk) | servicios_base
                servicios_qs = servicios_qs.distinct()

        form = CobroForm(request.POST)
        # asignar el queryset al campo antes de validar
        form.fields['servicio'].queryset = servicios_qs

        if form.is_valid():
            dni = form.cleaned_data['dni'].strip()
            cliente = get_object_or_404(Cliente.objects.exclude(nombre="-----"), dni=dni)
            membresia = Membresia.objects.filter(cliente=cliente).select_related('servicio').first()
            if not membresia:
                messages.error(request, "El cliente no tiene ninguna membresía registrada.")
                return render(request, 'cobro_nuevo.html', {'form': form, 'caja': caja})

            servicio = form.cleaned_data.get('servicio') or membresia.servicio

            # actualizar membresía
            membresia.clases_restantes = servicio.cantidad_clases
            membresia.fecha_fin = timezone.now().date() + timezone.timedelta(days=30)
            if not membresia.activa:
                membresia.activa = True
            membresia.save()

            cobro = form.save(commit=False)
            cobro.caja = caja
            cobro.cliente = cliente
            cobro.servicio = servicio
            cobro.total = servicio.precio
            if cobro.descripcion.strip() == "":
                cobro.detalle = f"Cobro por membresía: {servicio.nombre}"
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

            caja.registrar_ingreso(servicio.precio)
            messages.success(request, f"Cobro registrado para {cliente}.")
            return redirect('cobros_lista')
    else:
        form = CobroForm()
        # asignar queryset para GET (lista de servicios sin "Por Clase")
        form.fields['servicio'].queryset = servicios_base

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
                descripcion="Cobro por una clase",
                fecha_hora=timezone.now()
            )

            # Crear detalle
            DetalleCobro.objects.create(
                cobro=cobro,
                servicio=servicio,
                monto=servicio.precio,
                metodoDePago=metodo_pago
            )
            # Actualizar caja
            caja.registrar_ingreso(servicio.precio)

            messages.success(request, f"Cobro por clase registrado (${servicio.precio}).")
            return redirect('cobros_lista')
    else:
        form = CobroClaseForm()

    return render(request, 'cobro_un_dia.html', {'form': form, 'caja': caja})   


@login_required
@caja_abierta_required
def lista_cobros(request):
    caja = Caja.objects.filter(estado='abierta', usuario=request.user).first()
    form = MembresiaInscripcionForm(request.POST)
    if not caja:
        messages.error(request, "No hay una caja abierta para mostrar los cobros.")
        return redirect('cobros_lista')  # o a donde quieras redirigir

    cobros = caja.cobros.select_related("cliente", "servicio").all()

    # Filtros
    query = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', '')

    if query:
        cobros = cobros.filter(
            Q(cliente__nombre__icontains=query) |
            Q(cliente__apellido__icontains=query) |
            Q(cliente__dni__icontains=query) |
            Q(cliente__apellido__icontains=query.split()[0], cliente__nombre__icontains=' '.join(query.split()[1:])) |
            Q(cliente__nombre__icontains=query.split()[0], cliente__apellido__icontains=' '.join(query.split()[1:]))
        )

    #  Ordenamientos
    if orden == 'fecha_desc':
        cobros = cobros.order_by('-fecha_hora')
    elif orden == 'fecha_asc':
        cobros = cobros.order_by('fecha_hora')
    elif orden == 'dni_desc':
        cobros = cobros.order_by('-cliente__dni')
    elif orden == 'dni_asc':
        cobros = cobros.order_by('cliente__dni')
    elif orden == 'nombre_asc':
        cobros = cobros.order_by('cliente__nombre')
    elif orden == 'nombre_desc':
        cobros = cobros.order_by('-cliente__nombre')
    elif orden == 'apellido_asc':
        cobros = cobros.order_by('cliente__apellido')
    elif orden == 'apellido_desc':
        cobros = cobros.order_by('-cliente__apellido')
    elif orden == 'apellido_nombre':
        cobros = cobros.order_by('cliente__apellido', 'cliente__nombre')
    elif orden == 'nombre_apellido':
        cobros = cobros.order_by('cliente__nombre', 'cliente__apellido')
    else:
        cobros = cobros.order_by('-fecha_hora')  # default
    #paginacion
    paginator = Paginator(cobros, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'cobros_lista.html', {
        'cobros': cobros,
        'caja': caja,
        'query': query,
        'orden': orden,
        'tipo': 'cobros',
        'page_obj': page_obj,
        'form' : form
    })

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
        clientes = Cliente.objects.filter(dni__icontains=q).exclude(nombre__iexact="-----")[:10]
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

@login_required
@caja_abierta_required
def mostrar_extracciones(request):
    caja = Caja.objects.filter(estado='abierta', usuario=request.user).first()
    form = MembresiaInscripcionForm(request.POST)
    if not caja:
        messages.error(request, "No hay una caja abierta para mostrar las extracciones.")
        return redirect('cobros_lista')

    extracciones = caja.extracciones.select_related('usuario').all()

    # Filtros
    query = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', '')

    if query:
        extracciones = extracciones.filter(
            Q(usuario__first_name__icontains=query) |
            Q(usuario__last_name__icontains=query) |
            Q(usuario__first_name__icontains=query.split()[0]) & Q(usuario__last_name__icontains=' '.join(query.split()[1:])) |
            Q(usuario__last_name__icontains=query.split()[0]) & Q(usuario__first_name__icontains=' '.join(query.split()[1:])) |
            Q(usuario__username__icontains=query)
        )

    # Ordenamientos
    if orden == 'fecha_desc':
        extracciones = extracciones.order_by('-fecha_hora')
    elif orden == 'fecha_asc':
        extracciones = extracciones.order_by('fecha_hora')
    elif orden == 'dni_desc':
        extracciones = extracciones.order_by('-empleado__dni')  # Asumiendo que el DNI está en username
    elif orden == 'dni_asc':
        extracciones = extracciones.order_by('empleado__dni')
    elif orden == 'nombre_asc':
        extracciones = extracciones.order_by('usuario__first_name')
    elif orden == 'nombre_desc':
        extracciones = extracciones.order_by('-usuario__first_name')
    elif orden == 'apellido_asc':
        extracciones = extracciones.order_by('usuario__last_name')
    elif orden == 'apellido_desc':
        extracciones = extracciones.order_by('-usuario__last_name')
    elif orden == 'apellido_nombre':
        extracciones = extracciones.order_by('usuario__last_name', 'usuario__first_name')
    elif orden == 'nombre_apellido':
        extracciones = extracciones.order_by('usuario__first_name', 'usuario__last_name')
    else:
        extracciones = extracciones.order_by('-fecha_hora')  # Default

    #  Paginación
    paginator = Paginator(extracciones, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'cobros_extracciones_lista.html', {
        'extracciones': extracciones,
        'caja': caja,
        'query': query,
        'orden': orden,
        'page_obj': page_obj,
        'form': form,
    })
    
@login_required
@caja_abierta_required
def extraccion_detalle(request, pk):
    extraccion = get_object_or_404(Extraccion, pk=pk)

    # Opcional: restringir acceso a la misma caja/usuario (descomentar si aplica)
    # if extraccion.caja.usuario != request.user and not request.user.is_staff:
    #     raise Http404

    context = {
        'extraccion': extraccion,
    }
    return render(request, 'extraccion_detalle.html', context)
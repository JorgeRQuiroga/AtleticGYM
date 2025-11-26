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

    # 1. FILTRO DE SERVICIOS: Agregamos .filter(activo=True)
    # Esto asegura que solo traiga servicios activos y excluya "Por Clase"
    servicios_base = Servicio.objects.filter(activo=True).exclude(nombre__iexact='Por Clase')

    if request.method == 'POST':
        raw_dni = request.POST.get('dni', '').strip()
        
        # 2. FILTRO DE CLIENTE (Búsqueda inicial): 
        # Agregamos .exclude(nombre="CLASE", apellido="UNA")
        cliente = Cliente.objects.filter(dni=raw_dni)\
                                 .exclude(nombre="Prueba")\
                                 .exclude(nombre="CLASE", apellido="UNA")\
                                 .first()
                                 
        membresia = None
        if cliente:
            membresia = Membresia.objects.filter(cliente=cliente).select_related('servicio').first()

        servicios_qs = servicios_base
        if membresia and membresia.servicio:
            if membresia.servicio.nombre.lower() == 'por clase':
                # Aquí también nos aseguramos que servicios_base ya viene filtrado por activo=True
                servicios_qs = Servicio.objects.filter(pk=membresia.servicio.pk) | servicios_base
                servicios_qs = servicios_qs.distinct()

        form = CobroForm(request.POST)
        form.fields['servicio'].queryset = servicios_qs

        if form.is_valid():
            dni = form.cleaned_data['dni'].strip()
            
            # 3. FILTRO DE CLIENTE (Obtención final):
            # Aplicamos el mismo exclude aquí para evitar errores si el DNI existe pero es del usuario prohibido
            cliente = get_object_or_404(
                Cliente.objects.exclude(nombre="-----").exclude(nombre="Clase", apellido="Una"), 
                dni=dni
            )
            
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
        form.fields['servicio'].queryset = servicios_base

    return render(request, 'cobro_nuevo.html', {'form': form, 'caja': caja})


# En cobros/views.py

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
            # Obtenemos el servicio "Por clase" (Asegúrate que exista en BD)
            servicio = Servicio.objects.filter(nombre__iexact="Por clase").first()
            
            if not servicio:
                messages.error(request, "El servicio 'Por clase' no está configurado en el sistema.")
                return redirect('cobros_lista')

            metodo_pago = form.cleaned_data['metodo_pago']

            # --- SOLUCIÓN AQUÍ ---
            # Usamos get_or_create para manejar si el DNI ya existe o es nuevo.
            # Los defaults usan 'Visitante' y 'Diario' para pasar el validador 'validar_nombre'
            # que solo acepta letras.
            cliente, created = Cliente.objects.get_or_create(
                dni=dni,
                defaults={
                    'nombre': "CLASE",      # Solo letras para pasar validación
                    'apellido': "UNA ",       # Solo letras para pasar validación
                    'telefono': "0000000000",   # Default válido
                    'emergencia': "",
                    'email': "",                # Email vacío es permitido por blank=True
                    'domicilio': "No especificado"
                }
            )

            # Crear el cobro asociado a este cliente (nuevo o existente)
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

            messages.success(request, f"Cobro por clase registrado (${servicio.precio}) a DNI {dni}.")
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
        clientes = Cliente.objects.filter(dni__icontains=q)\
                                  .exclude(nombre__iexact="-----")\
                                  .exclude(nombre="CLASE", apellido="UNA")[:10]
        
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
    if orden == "fecha_desc":
        extracciones = extracciones.order_by("-fecha_hora")
    elif orden == "fecha_asc":
        extracciones = extracciones.order_by("fecha_hora")
    elif orden == "monto_desc":
        extracciones = extracciones.order_by("-monto")
    elif orden == "monto_asc":
        extracciones = extracciones.order_by("monto") # Default

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
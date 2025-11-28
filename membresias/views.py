from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import MembresiaInscripcionForm, MembresiaEdicionForm
from .models import Membresia
from cobros.decorators import caja_abierta_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from cobros.models import Cobro, DetalleCobro, MetodoDePago
from cajas.models import Caja
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from login.decorators import group_required
from django.db import transaction
from django.utils import timezone


@login_required
@caja_abierta_required
def inscribir_cliente(request):
    caja = Caja.objects.filter(estado='abierta', usuario=request.user).first()
    if not caja:
        messages.error(request, "No hay una caja abierta para registrar el cobro.")
        return redirect('membresias:membresias_lista')

    if request.method == 'POST':
        form = MembresiaInscripcionForm(request.POST)
        if form.is_valid():
            # Obtener DNI directamente del formulario limpio
            dni = form.cleaned_data.get('dni')
            
            if not dni:
                messages.error(request, "El DNI es obligatorio.")
                return redirect('membresias:membresias_lista')

            # Comprobar si ya existe una membresía activa para ese DNI
            tiene_activa = Membresia.objects.filter(cliente__dni=dni, activa=True).exists()
            if tiene_activa:
                messages.error(request, f"Ya existe una membresía activa para el DNI {dni}.")
                # Renderizar nuevamente el formulario con el error
                membresias = Membresia.objects.select_related('cliente', 'servicio').all()
                return render(request, 'membresias_lista.html', {
                    'form': form,
                    'membresias': membresias,
                    'caja': caja
                })

            # Buscar si existe alguna membresía inactiva para reactivar (la más reciente)
            membresia_inactiva = Membresia.objects.filter(
                cliente__dni=dni, 
                activa=False
            ).order_by('-fecha_fin', '-id').first()

            # Guardar o reactivar dentro de una transacción
            with transaction.atomic():
                if membresia_inactiva:
                    # Reactivar membresía existente
                    membresia = membresia_inactiva
                    
                    # Actualizar datos del cliente
                    cliente = membresia.cliente
                    cliente.nombre = form.cleaned_data['nombre']
                    cliente.apellido = form.cleaned_data['apellido']
                    cliente.telefono = form.cleaned_data['telefono']
                    cliente.emergencia = form.cleaned_data.get('emergencia', '')
                    cliente.domicilio = form.cleaned_data.get('domicilio', '')
                    cliente.email = form.cleaned_data.get('email', '')
                    cliente.save()
                    
                    # Actualizar datos de la membresía
                    servicio = form.cleaned_data['servicio']
                    membresia.servicio = servicio
                    membresia.fecha_inicio = timezone.now().date()
                    membresia.fecha_fin = timezone.now().date() + timezone.timedelta(days=30)
                    membresia.clases_restantes = getattr(servicio, 'cantidad_clases', 0)
                    membresia.activa = True
                    membresia.observaciones = form.cleaned_data.get('observaciones', 'Ninguna')
                    membresia.save()
                    
                    mensaje_tipo = 'reactivada'
                else:
                    # Crear nueva membresía
                    membresia = form.save()
                    mensaje_tipo = 'creada'

                # Crear el cobro automáticamente
                servicio = membresia.servicio
                cobro = Cobro.objects.create(
                    caja=caja,
                    cliente=membresia.cliente,
                    servicio=servicio,
                    total=servicio.precio,
                    descripcion=f"Inscripción a {servicio.nombre}"
                )

                # Obtener método de pago desde el formulario
                metodo_pago_id = request.POST.get('metodo_pago')
                if metodo_pago_id:
                    metodo_pago = get_object_or_404(MetodoDePago, id=metodo_pago_id)
                else:
                    metodo_pago = MetodoDePago.objects.get_or_create(metodoDePago="Efectivo")[0]

                # Crear detalle del cobro
                DetalleCobro.objects.create(
                    cobro=cobro,
                    servicio=servicio,
                    monto=cobro.total,
                    metodoDePago=metodo_pago
                )

                # Actualizar saldo de la caja
                caja.total_en_caja += cobro.total
                caja.save()

            messages.success(
                request,
                f"Membresía {mensaje_tipo} y cobro registrado para "
                f"{membresia.cliente.apellido}, {membresia.cliente.nombre}. Vence el {membresia.fecha_fin} "
                f"con {membresia.clases_restantes} clases asignadas."
            )
            return redirect('membresias:membresias_lista')
        else:
            messages.error(request, "Error en el formulario. Verifica los datos.")
    else:
        form = MembresiaInscripcionForm()

    membresias = Membresia.objects.select_related('cliente', 'servicio').all()
    return render(request, 'membresias_lista.html', {
        'form': form,
        'membresias': membresias,
        'caja': caja
    })


@login_required
def lista_membresias(request):
    # Base queryset
    membresias = Membresia.objects.select_related('cliente', 'servicio').order_by('-activa', 'id')

    # --- Búsqueda ---
    query = request.GET.get('q')
    if query:
        terms = query.split()
        for term in terms:
            membresias = membresias.filter(
                Q(cliente__dni__icontains=term) |
                Q(cliente__nombre__icontains=term) |
                Q(cliente__apellido__icontains=term)
            )

    # --- Ordenamiento ---
    orden = request.GET.get('orden')
    if orden == 'fecha_asc':
        membresias = membresias.order_by('id')
    elif orden == 'fecha_desc':
        membresias = membresias.order_by('-id')
    elif orden == 'nombre_asc':
        membresias = membresias.order_by('cliente__apellido', 'cliente__nombre')
    elif orden == 'nombre_desc':
        membresias = membresias.order_by('-cliente__apellido', '-cliente__nombre')
    elif orden == 'dni_asc':
        membresias = membresias.order_by('cliente__dni')
    elif orden == 'dni_desc':
        membresias = membresias.order_by('-cliente__dni')
    elif orden == 'solo_activo':
        membresias = membresias.filter(activa=True)
    elif orden == 'solo_inactivo':
        membresias = membresias.filter(activa=False)
    else:
        # Por defecto: primero activas, luego inactivas
        membresias = membresias.order_by('-id', '-activa')


    # --- Paginación ---
    paginator = Paginator(membresias, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = MembresiaInscripcionForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Membresía registrada correctamente.")
                return redirect('membresias_lista')
            except Exception as e:
                # Si falla el save() (ej. DNI duplicado al crear Cliente), capturamos el error
                form.add_error(None, f"Error al guardar: {e}")
    else:
        form = MembresiaInscripcionForm()

    return render(request, 'membresias_lista.html', {
        'page_obj': page_obj,
        'query': query,
        'orden': orden,
        'form': form,
        'membresias': membresias,
    })
    
    
@login_required
def borrar_membresia(request, membresia_id):
    try:
        membresia = Membresia.objects.get(id=membresia_id)
        membresia.borrar()
        messages.success(request, "Membresía eliminada correctamente.")
    except Membresia.DoesNotExist:
        messages.error(request, "La membresía no existe.")
    return redirect('membresias:membresias_lista')


@login_required
def menu(request):
    if request.method == 'POST':
        form = MembresiaInscripcionForm(request.POST)
        if form.is_valid():
            membresia = form.save()
            messages.success(request, f"Cliente {membresia.cliente} inscrito con éxito en {membresia.servicio}.")
            return render(request, 'membresias_menu.html')        
        else:
            messages.error(request, "Error en el formulario. Verifica los datos.")
    else:
        form = MembresiaInscripcionForm()
    return render(request, 'membresias_menu.html', {'form': form})


@login_required
def membresias_detalle(request, pk):
    membresia = get_object_or_404(Membresia.objects.select_related('cliente', 'servicio'), pk=pk)

    # Crear formulario de edición precargado con los datos
    form = MembresiaEdicionForm(instance=membresia)

    return render(request, 'membresias_detalle.html', {
        'membresia': membresia,
        'form': form,
    })

    
@login_required
def membresias_editar(request, pk):
    membresia = get_object_or_404(Membresia.objects.select_related('cliente', 'servicio'), pk=pk)

    if request.method == 'POST':
        form = MembresiaEdicionForm(request.POST, instance=membresia)
        
        # Si es AJAX, responder con JSON
        es_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        if form.is_valid():
            # Guardar cambios en el cliente y la membresía
            form.save()
            
            # Recalcular clases_restantes si cambió el servicio
            if membresia.servicio.cantidad_clases > 0:
                membresia.clases_restantes = membresia.servicio.cantidad_clases
                membresia.save()

            if es_ajax:
                return JsonResponse({
                    'ok': True, 
                    'message': 'Membresía actualizada correctamente.'
                })
            else:
                messages.success(request, "Membresía actualizada correctamente.")
                return redirect('membresias:membresias_detalle', pk=membresia.pk)
        else:
            # Si hay errores en el formulario
            if es_ajax:
                return JsonResponse({
                    'ok': False,
                    'errors': form.errors
                })
            else:
                messages.error(request, "Error al actualizar. Verifica los datos.")
                
    else:
        form = MembresiaEdicionForm(instance=membresia)

    return render(request, 'membresias_detalle.html', {
        'form': form,
        'membresia': membresia,
    })


@login_required
def membresia_editar_partial(request, pk):
    """Vista para cargar el formulario de edición vía AJAX (ya no es necesaria)"""
    membresia = get_object_or_404(Membresia.objects.select_related('cliente', 'servicio'), pk=pk)

    if request.method == 'POST':
        form = MembresiaEdicionForm(request.POST, instance=membresia)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'message': 'Membresía actualizada.'})
            messages.success(request, "Membresía actualizada correctamente.")
            return redirect('membresias:membresias_detalle', pk=membresia.pk)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string(
                    'partials/_form.html',
                    {'form': form, 'membresia': membresia},
                    request=request
                )
                return JsonResponse({'ok': False, 'html': html})
    else:
        form = MembresiaEdicionForm(instance=membresia)

    html = render_to_string(
        'partials/_form.html',
        {'form': form, 'membresia': membresia},
        request=request
    )
    return HttpResponse(html)
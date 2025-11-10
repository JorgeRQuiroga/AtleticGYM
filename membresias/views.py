from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import MembresiaInscripcionForm
from .models import Membresia
from cobros.decorators import caja_abierta_required
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from membresias.forms import MembresiaInscripcionForm
from .models import Membresia
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
            # Creamos una instancia temporal para leer los campos sin guardar
            temp_memb = form.save(commit=False)

            # Obtener cliente y DNI de forma robusta
            cliente = getattr(temp_memb, 'cliente', None) or form.cleaned_data.get('cliente')
            dni = None
            if cliente:
                dni = getattr(cliente, 'dni', None)
            if not dni:
                dni = form.cleaned_data.get('dni') or request.POST.get('dni')

            # Comprobar si ya existe una membresía activa para ese DNI
            if dni:
                tiene_activa = Membresia.objects.filter(cliente__dni=dni, activa=True).exists()
                if tiene_activa:
                    messages.error(request, "Ya existe una membresía activa para ese DNI.")
                    return redirect('membresias:membresias_lista')

                # Buscar si existe alguna membresía inactiva para reactivar (la más reciente)
                membresia_inactiva = Membresia.objects.filter(cliente__dni=dni, activa=False).order_by('-fecha_fin', '-id').first()
            else:
                membresia_inactiva = None

            # Guardar o reactivar dentro de una transacción
            with transaction.atomic():
                if membresia_inactiva:
                    # Reactivar: actualizar campos relevantes con los del formulario temporal
                    membresia = membresia_inactiva
                    # Actualizar servicio y fechas/clases según lo enviado en el form
                    membresia.servicio = temp_memb.servicio
                    membresia.fecha_inicio = temp_memb.fecha_inicio or timezone.now()
                    membresia.fecha_fin = temp_memb.fecha_fin
                    # Si el formulario calcula clases_restantes, usarlo; si no, recalcular según servicio
                    if hasattr(temp_memb, 'clases_restantes') and temp_memb.clases_restantes is not None:
                        membresia.clases_restantes = temp_memb.clases_restantes
                    else:
                        # ejemplo: si servicio tiene cantidad_clases
                        if getattr(membresia.servicio, 'cantidad_clases', None):
                            membresia.clases_restantes = membresia.servicio.cantidad_clases
                    membresia.activa = True
                    # actualizar otros campos que el formulario pudiera haber enviado
                    # (por ejemplo: precio, observaciones, etc.)
                    for field in ['precio', 'observaciones']:
                        if hasattr(temp_memb, field):
                            setattr(membresia, field, getattr(temp_memb, field))
                    membresia.save()
                else:
                    # No hay inactiva: crear nueva membresía como antes
                    membresia = form.save()

                # Crear el cobro automáticamente (se cobra tanto en nueva inscripción como en reactivación)
                servicio = membresia.servicio
                cobro = Cobro.objects.create(
                    caja=caja,
                    cliente=membresia.cliente,
                    servicio=servicio,
                    total=servicio.precio,
                    descripcion=f"Inscripción a {servicio.nombre}"
                )

                # Obtener método de pago desde el formulario (ej: un select en el form)
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
                f"Membresía {'reactivada' if membresia_inactiva else 'creada'} y cobro registrado para "
                f"{membresia.cliente.apellido}, {membresia.cliente.nombre}. Vence el {membresia.fecha_fin} "
                f"con {membresia.clases_restantes} clases asignadas."
            )
            return redirect('membresias_lista')
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
    form = MembresiaInscripcionForm()
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
        membresias = membresias.order_by('-activa', 'cliente__apellido')

    # --- Paginación ---
    paginator = Paginator(membresias, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'membresias_lista.html', {
        'page_obj': page_obj,   # Usar solo esto en el template
        'query': query,
        'orden': orden,
        'form': form,
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

    # si querés mostrar el form precargado en el modal:
    form = MembresiaInscripcionForm(membresia_instance=membresia)

    return render(request, 'membresias_detalle.html', {
        'membresia': membresia,
        'form': form,
    })
    
@login_required
def membresias_editar(request, pk):
    membresia = get_object_or_404(
        Membresia.objects.select_related('cliente', 'servicio'), pk=pk
    )

    if request.method == 'POST':
        form = MembresiaInscripcionForm(request.POST, instance=membresia)
        if form.is_valid():
            membresia = form.save()  # devuelve la instancia actualizada

            # 🔧 recalcular clases_restantes en base al servicio
            if membresia.servicio.cantidad_clases > 0:
                membresia.clases_restantes = membresia.servicio.cantidad_clases
                membresia.save()

            messages.success(request, "Membresía actualizada correctamente.")
            return redirect('membresias:membresias_detalle', pk=membresia.pk)
    else:
        form = MembresiaInscripcionForm(instance=membresia)

    return render(request, 'membresias_detalle.html', {
        'form': form,
        'membresia': membresia,
    })

@login_required
def membresia_editar_partial(request, pk):
    membresia = get_object_or_404(Membresia.objects.select_related('cliente', 'servicio'), pk=pk)

    if request.method == 'POST':
        form = MembresiaInscripcionForm(request.POST, instance=membresia)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'message': 'Membresía actualizada.'})
            messages.success(request, "Membresía actualizada correctamente.")
            return redirect('membresias:membresia_detalle', pk=membresia.pk)
        else:
            # si es AJAX devolver el HTML con errores para reinyectar
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('membresias/partials/_form.html', {'form': form, 'membresia': membresia}, request=request)
                return JsonResponse({'ok': False, 'html': html})
    else:
        form = MembresiaInscripcionForm(instance=membresia)

    html = render_to_string('partials/_form.html', {'form': form, 'membresia': membresia}, request=request)
    return HttpResponse(html)

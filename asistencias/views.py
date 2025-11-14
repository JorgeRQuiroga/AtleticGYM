from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
from .models import Asistencia
from membresias.models import Membresia
from datetime import timedelta
from django.db.models import Q
from django.utils.dateparse import parse_date


@login_required
def asistencia_opciones(request):
    # Vista que simplemente renderiza la página del menú de opciones de asistencia.
    return render(request, 'asistencia_opciones.html')

def registrar_asistencia(request):
    template_name = 'asistencia_registrar.html'

    if request.method == 'GET':
        return render(request, template_name)

    elif request.method == 'POST':
        dni_str = request.POST.get('dni', '').strip()
        dni_str = dni_str.replace('.', '').replace('-', '')

        try:
            dni = int(dni_str)
        except ValueError:
            messages.error(request, 'Por favor, ingrese un DNI válido (solo números).')
            return redirect('asistencias:asistencia_registrar')

        try:
            membresia = Membresia.objects.select_related('cliente', 'servicio').get(cliente__dni=dni)
        except Membresia.DoesNotExist:
            messages.error(request, f'No se encontró ninguna membresía para el DNI {dni}.')
            return redirect('asistencias:asistencia_registrar')

        hoy = timezone.now().date()

        # Validar membresía activa
        if not membresia.activa or membresia.fecha_fin < hoy:
            messages.warning(request, f'Hola {membresia.cliente.nombre}, tu membresía no está activa.')
            return redirect('asistencias:asistencia_registrar')

        # Registrar asistencia
        Asistencia.objects.create(membresia=membresia, fecha_hora=timezone.now())

        # Actualizar clases restantes si corresponde
        if membresia.servicio.cantidad_clases > 0:
            membresia.clases_restantes -= 1
            membresia.save()

        messages.success(request, f"Asistencia registrada correctamente para {membresia.cliente.nombre}.")
        return redirect('asistencias:asistencia_registrar')
           
@login_required
def lista_asistencias(request):
    busqueda = request.GET.get('busqueda', '').strip()
    fecha_str = request.GET.get('fecha', '').strip()
    orden = request.GET.get('orden', '')

    asistencias = Asistencia.objects.select_related('membresia__cliente', 'membresia__servicio')

    if busqueda:
        asistencias = asistencias.filter(
            Q(membresia__cliente__nombre__icontains=busqueda) |
            Q(membresia__cliente__apellido__icontains=busqueda)
        )

    if fecha_str:
        fecha = parse_date(fecha_str)
        if fecha:
            asistencias = asistencias.filter(fecha_hora__date=fecha)

    # Ordenamientos
    if orden == 'nombre_asc':
        asistencias = asistencias.order_by('membresia__cliente__nombre')
    elif orden == 'nombre_desc':
        asistencias = asistencias.order_by('-membresia__cliente__nombre')
    elif orden == 'clases_asc':
        asistencias = asistencias.order_by('membresia__clases_restantes')
    elif orden == 'clases_desc':
        asistencias = asistencias.order_by('-membresia__clases_restantes')
    elif orden == 'fecha_asc':
        asistencias = asistencias.order_by('fecha_hora')
    else:
        asistencias = asistencias.order_by('-fecha_hora')

    asistencias = asistencias[:100]

    return render(request, 'asistencia_lista.html', {
        'asistencias': asistencias,
        'busqueda': busqueda,
        'fecha': fecha_str,
        'orden': orden,
    })
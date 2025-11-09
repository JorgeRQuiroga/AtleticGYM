from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import MembresiaInscripcionForm
from .models import Membresia
from cobros.decorators import caja_abierta_required
from django.db.models import Q
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import date, timedelta


@login_required
@caja_abierta_required
def inscribir_cliente(request):
    if request.method == 'POST':
        form = MembresiaInscripcionForm(request.POST)
        if form.is_valid():
            membresia = form.save()
            messages.success(
                request,
                f"Membresía creada para {membresia.cliente.apellido}, {membresia.cliente.nombre}. "
                f"Vence el {membresia.fecha_fin} con {membresia.clases_restantes} clases asignadas."
            )
            return redirect('membresias:membresias_lista')
        else:
            messages.error(request, "Error en el formulario. Verifica los datos.")
    else:
        form = MembresiaInscripcionForm()
    membresias = Membresia.objects.select_related('cliente', 'servicio').all()
    return render(request, 'membresia_form.html', {'form': form, 'membresias': membresias})

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
        membresias = membresias.order_by('id')  # más antiguo primero
    elif orden == 'fecha_desc':
        membresias = membresias.order_by('-id')  # más nuevo primero
    elif orden == 'nombre_asc':
        membresias = membresias.order_by('cliente__apellido', 'cliente__nombre')
    elif orden == 'nombre_desc':
        membresias = membresias.order_by('-cliente__apellido', '-cliente__nombre')
    elif orden == 'dni_asc':
        membresias = membresias.order_by('cliente__dni')
    elif orden == 'dni_desc':
        membresias = membresias.order_by('-cliente__dni')

    return render(request, 'membresias_lista.html', {
        'membresias': membresias,
        'query': query,
        'orden': orden,
        'form' : form
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
def buscar_membresia_por_dni(request):
    """
    Busca una membresía de cliente por DNI y muestra sus detalles y acciones.
    Prioriza la membresía activa si existen múltiples para el mismo DNI.
    """
    membresia = None
    query_dni = request.GET.get('dni', '').strip()

    if query_dni:
        try:
            # Busca la membresía más relevante (activa y con fecha de fin más lejana)
            membresia = Membresia.objects.select_related('cliente', 'servicio').filter(cliente__dni=query_dni).order_by('-activa', '-fecha_fin').first()
            if not membresia:
                messages.warning(request, f"No se encontró ninguna membresía para el DNI {query_dni}.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error al buscar la membresía: {e}")

    context = {'membresia': membresia, 'query_dni': query_dni}
    return render(request, 'membresia_buscar.html', context)


def grafico_membresias(request):
    # --- 1. Distribución de membresías activas ---
    distribucion = (
        Membresia.objects
        .filter(activa=True)
        .values('servicio__nombre')
        .annotate(total=Count('id'))
        .order_by('servicio__nombre')
    )
    labels_membresias = [d['servicio__nombre'] for d in distribucion]
    data_membresias = [d['total'] for d in distribucion]
 
    # --- 2. Altas vs Bajas mensuales últimos 12 meses ---
    hoy = date.today()
    hace_un_anio = hoy - timedelta(days=365)
 
    # Altas por mes
    altas = (
        Membresia.objects
        .filter(fecha_inicio__gte=hace_un_anio)
        .annotate(mes=TruncMonth('fecha_inicio'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
 
    # Bajas por mes (cuando se desactivan)
    bajas = (
        Membresia.objects
        .filter(activa=False, fecha_fin__gte=hace_un_anio)
        .annotate(mes=TruncMonth('fecha_fin'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    meses = [a['mes'].strftime("%b %Y") for a in altas]
    altas_data = [a['total'] for a in altas]
    bajas_data = [b['total'] for b in bajas]
    
    # --- Combinación de datos para alinear meses ---
    # Creamos un diccionario para cada mes de los últimos 12
    meses_dict = {}
    for i in range(12):
        mes_actual = (hoy.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        meses_dict[mes_actual.strftime('%Y-%m')] = {'altas': 0, 'bajas': 0}

    # Llenamos con los datos de altas
    for alta in altas:
        mes_key = alta['mes'].strftime('%Y-%m')
        if mes_key in meses_dict:
            meses_dict[mes_key]['altas'] = alta['total']

    # Llenamos con los datos de bajas
    for baja in bajas:
        mes_key = baja['mes'].strftime('%Y-%m')
        if mes_key in meses_dict:
            meses_dict[mes_key]['bajas'] = baja['total']

    meses_ordenados = sorted(meses_dict.keys())
    # Render
    context = {
        'labels_membresias': labels_membresias,
        'data_membresias': data_membresias,
        'meses': meses,
        'altas_data': altas_data,
        'bajas_data': bajas_data,
        'meses': [date.fromisoformat(m + '-01').strftime('%b %Y') for m in meses_ordenados],
        'altas_data': [meses_dict[m]['altas'] for m in meses_ordenados],
        'bajas_data': [meses_dict[m]['bajas'] for m in meses_ordenados],

    }
    return render(request, 'grafico_membresias.html', context)

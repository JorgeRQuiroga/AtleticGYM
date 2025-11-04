from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import MembresiaInscripcionForm
from .models import Membresia
from cobros.decorators import caja_abierta_required
from django.db.models import Q

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


def grafico_membresias(request):
    return render(request, 'grafico_membresias.html')

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
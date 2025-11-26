# empleados/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Empleado
from .forms import EmpleadoForm
from django.contrib.auth.models import User, Group
from empleados.forms import EmpleadoForm
from django.db import transaction
from datetime import date
from login.decorators import group_required

@login_required
@group_required("Duenio")
def empleado_menu(request):
    form = EmpleadoForm()
    return render(request, 'empleado_menu.html', {'form': form})

# --- Listar con búsqueda ---
@login_required
@group_required("Duenio")
def empleado_lista(request):
    form = EmpleadoForm()
    query = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', '')  # nuevo parámetro para ordenar
    empleados = Empleado.objects.filter(activo=True)

    # 🔎 Filtros de búsqueda
    if query:
        partes = query.split()
        if len(partes) == 2:
            # Si el usuario escribe "Apellido Nombre"
            empleados = empleados.filter(
                Q(apellido__icontains=partes[0], nombre__icontains=partes[1]) |
                Q(nombre__icontains=partes[0], apellido__icontains=partes[1])
            )
        else:
            empleados = empleados.filter(
                Q(nombre__icontains=query) |
                Q(apellido__icontains=query) |
                Q(dni__icontains=query)
            )

    # 🔧 Ordenamientos
    if orden == 'nombre_asc':
        empleados = empleados.order_by('nombre')
    elif orden == 'nombre_desc':
        empleados = empleados.order_by('-nombre')
    elif orden == 'apellido_asc':
        empleados = empleados.order_by('apellido')
    elif orden == 'apellido_desc':
        empleados = empleados.order_by('-apellido')
    elif orden == 'dni_asc':
        empleados = empleados.order_by('dni')
    elif orden == 'dni_desc':
        empleados = empleados.order_by('-dni')
    elif orden == 'fecha_asc':
        empleados = empleados.order_by('fecha_hora_alta')
    elif orden == 'fecha_desc':
        empleados = empleados.order_by('-fecha_hora_alta')
    else:
        # Orden por defecto
        empleados = empleados.order_by('-fecha_hora_alta')

    # 📑 Paginación
    paginator = Paginator(empleados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'empleado_lista.html', {
        'page_obj': page_obj,
        'query': query,
        'orden': orden,
        'form': form
    })

# # --- Agregar ---
@login_required
@group_required("Duenio")
def empleado_agregar(request):
    """Vista para registrar un nuevo empleado o reactivar uno existente"""
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    dni = form.cleaned_data['dni']
                    nombre = form.cleaned_data['nombre']
                    apellido = form.cleaned_data['apellido']
                    telefono = form.cleaned_data.get('telefono', '')
                    domicilio = form.cleaned_data.get('domicilio', '')

                    # Verificar si el empleado ya existe
                    empleado_existente = Empleado.objects.filter(dni=dni).first()
                    if empleado_existente:
                        if not empleado_existente.activo:
                            # Reactivar empleado
                            empleado_existente.activo = True
                            empleado_existente.fecha_baja = None
                            empleado_existente.nombre = nombre
                            empleado_existente.apellido = apellido
                            empleado_existente.telefono = telefono
                            empleado_existente.domicilio = domicilio
                            empleado_existente.save()
                            messages.success(request, f'Empleado {nombre} {apellido} reactivado exitosamente.')
                        else:
                            messages.warning(request, f'El empleado con DNI {dni} ya existe y está activo.')
                        return redirect('empleado_lista')

                    # Crear nuevo usuario con DNI como username
                    user = User.objects.create_user(
                        username=dni,
                        first_name=nombre,
                        last_name=apellido,
                        password=dni,
                    )
                    grupo_empleado, created = Group.objects.get_or_create(name="Empleado")
                    user.groups.add(grupo_empleado)
                    user.save()

                    # Crear nuevo empleado usando datos validados
                    empleado = form.save(commit=False)
                    empleado.user = user
                    empleado.save()

                    messages.success(request, f'Empleado {nombre} {apellido} registrado exitosamente.')
                    return redirect('empleado_lista')

            except Exception as e:
                messages.error(request, f'Error al registrar el empleado: {str(e)}')
        else:
            # Si el form no es válido, mostrar errores
            messages.error(request, "Hay errores en el formulario. Verifique los datos ingresados.")
    else:
        form = EmpleadoForm()
    
    return render(request, 'empleado_lista.html',
                  {'form': form,
                   })

# --- Editar ---
@login_required
@group_required("Duenio")
def empleado_editar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, "Empleado actualizado correctamente.")
            return redirect('empleado_lista')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'empleado_form.html', {'form': form, 'empleado': empleado})

# --- Eliminar ---
@login_required
@group_required("Duenio")
def empleado_eliminar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.dar_baja()
        messages.success(request, "Empleado eliminado correctamente.")
        return redirect('empleado_lista')
    return render(request, 'empleado_eliminar.html', {'empleado': empleado})
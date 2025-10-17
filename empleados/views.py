# empleados/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Empleado
from .forms import EmpleadoForm
from django.contrib.auth.models import User

@login_required
def empleado_menu(request):
    return render(request, 'empleados:empleado_menu.html')

# --- Listar con búsqueda ---
@login_required
def empleado_lista(request):
    query = request.GET.get('q', '')
    empleados = Empleado.objects.all()

    if query:
        empleados = empleados.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(dni__icontains=query)
        )

    # 👇 importante: ordenar sobre el queryset filtrado, no volver a all()
    empleados = empleados.order_by('-fecha_hora_alta')

    paginator = Paginator(empleados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'empleado_lista.html', {
        'page_obj': page_obj,
        'query': query
    })


# --- Agregar ---
@login_required
def empleado_agregar(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            empleado = Empleado.objects.filter(dni=dni).first()

            if empleado and getattr(empleado, "activo", True):
                messages.error(request, "Ya existe un empleado activo con ese DNI.")
                return redirect('empleados:empleado_lista')

            elif empleado and not getattr(empleado, "activo", True):
                empleado.activo = True
                empleado.fecha_baja = None
                empleado.save()
                messages.success(request, f"Empleado {empleado.nombre} {empleado.apellido} reactivado correctamente.")
                return redirect('empleados:empleado_lista')

            else:
                empleado = form.save(commit=False)
                if not empleado.user:
                    empleado.user = User.objects.create_user(
                        username=empleado.dni,
                        password="contraseña_temporal",
                        first_name=empleado.nombre,
                        last_name=empleado.apellido
                    )
                empleado.save()

                grupo = form.cleaned_data.get('grupo')
                if grupo and empleado.user:
                    empleado.user.groups.clear()
                    empleado.user.groups.add(grupo)

                messages.success(request, "Empleado registrado correctamente.")
                return redirect('empleados:empleados:empleado_lista')
    else:
        form = EmpleadoForm()

    return render(request, 'empleado_form.html', {'form': form})

# --- Editar ---
@login_required
def empleado_editar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, "Empleado actualizado correctamente.")
            return redirect('empleados:empleado_lista')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'empleado_form.html', {'form': form, 'empleado': empleado})

# --- Eliminar ---
@login_required
def empleado_eliminar(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.dar_baja()
        messages.success(request, "Empleado eliminado correctamente.")
        return redirect('empleados:empleado_lista')
    return render(request, 'empleado_eliminar.html', {'empleado': empleado})
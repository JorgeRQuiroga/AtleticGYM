# empleados/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Empleado
from .forms import EmpleadoForm
from django.contrib.auth.models import User
from django.db import transaction
from datetime import date

@login_required
def empleado_menu(request):
    form = EmpleadoForm()
    return render(request, 'empleado_menu.html', {'form': form})

# --- Listar con búsqueda ---
@login_required
def empleado_lista(request):
    form = EmpleadoForm()
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
        'query': query,
        'form' : form
    })


# # --- Agregar ---
@login_required
@transaction.atomic
def empleado_agregar(request):
    empleado_existente = None
    
    if request.method == 'POST':
        # Verificar si es una recontratación confirmada
        recontratar = request.POST.get('recontratar')
        dni = request.POST.get('dni')
        
        if recontratar == 'si':
            # Reactivar empleado existente
            try:
                empleado = Empleado.objects.get(dni=dni, activo=False)
                empleado.activo = True
                empleado.fecha_baja = None
                empleado.fecha_ingreso = date.today()
                empleado.usuario.is_active = True
                # empleado.usuario.save()
                
                # Actualizar datos del formulario
                empleado.nombre = request.POST.get('nombre')
                empleado.apellido = request.POST.get('apellido')
                empleado.telefono = request.POST.get('telefono')
                
                # Actualizar usuario
                empleado.usuario.first_name = empleado.nombre
                empleado.usuario.last_name = empleado.apellido
                empleado.usuario.save()
                
                empleado.save()
                
                messages.success(request, f'Empleado {empleado.nombre_completo()} recontratado exitosamente. Usuario: {dni}, Contraseña: {dni}')
                return redirect('lista_empleados')
            except Empleado.DoesNotExist:
                messages.error(request, 'Error al recontratar el empleado.')
                return redirect('empleados:agregar_empleado')
        
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            
            # Verificar si existe un empleado inactivo con ese DNI
            try:
                empleado_existente = Empleado.objects.get(dni=dni, activo=False)
                # Si existe un empleado inactivo, mostrar confirmación
                context = {
                    'form': form,
                    'accion': 'Agregar',
                    'empleado_existente': empleado_existente,
                    'mostrar_confirmacion': True
                }
                return render(request, 'empleado_form.html', context)
            except Empleado.DoesNotExist:
                pass
            
            # Si no existe empleado inactivo, crear nuevo empleado
            empleado = form.save(commit=False)
            
            try:
                usuario = User.objects.create_user(
                    username=dni,
                    password=dni,
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['nombre'],
                    last_name=form.cleaned_data['apellido']
                )
                empleado.usuario = usuario
                empleado.save()
                
                messages.success(request, f'Empleado {empleado.nombre_completo()} agregado exitosamente. Usuario: {dni}, Contraseña: {dni}')
                return redirect('empleados:lista_empleados')
            except Exception as e:
                messages.error(request, f'Error al crear el empleado: {str(e)}')
    else:
        form = EmpleadoForm()
    
    return render(request, 'empleado_form.html', {'form': form, 'accion': 'Agregar'})

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
        return redirect('empleado_lista')
    return render(request, 'empleado_eliminar.html', {'empleado': empleado})
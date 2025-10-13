# clientes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Cliente
from .forms import ClienteForm

@login_required
def cliente_menu(request):
    return render(request, 'cliente_menu.html')

@login_required
def cliente_listar(request):
    estado = request.GET.get('estado')
    buscador = request.GET.get('buscador', '').strip()

    clientes = Cliente.objects.all().order_by('dni')

    if estado == 'activo':
        clientes = clientes.filter(membresia_activa=True)
    elif estado == 'inactivo':
        clientes = clientes.filter(membresia_activa=False)

    if buscador:
        clientes = clientes.filter(
            Q(nombre__icontains=buscador) |
            Q(apellido__icontains=buscador) |
            Q(dni__icontains=buscador) |
            Q(telefono__icontains=buscador) |
            Q(email__icontains=buscador) |
            Q(servicio__nombre__icontains=buscador)
        ).distinct()

    paginator = Paginator(clientes, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'estado': estado,
        'buscador': buscador,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/clientes_grid.html', context)

    return render(request, 'cliente_listar.html', context)

@login_required
def cliente_agregar(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente agregado correctamente.")
            return redirect('cliente_listar')
        messages.error(request, "Error al guardar. Verificá los datos.")
    else:
        form = ClienteForm()
    return render(request, 'cliente_agregar.html', {'form': form})

@login_required
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente actualizado.")
            return redirect('cliente_listar')
        messages.error(request, "Error al actualizar. Revisá el formulario.")
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'cliente_editar.html', {'form': form, 'cliente': cliente})

@login_required
def cliente_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, "Cliente eliminado.")
        return redirect('cliente_listar')
    return render(request, 'cliente_eliminar.html', {'cliente': cliente})
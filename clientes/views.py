<<<<<<< HEAD
from django.shortcuts import render

# Create your views here.
=======
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.views import es_admin
from .models import Cliente
from .forms import ClienteForm

@login_required
def cliente_listar(request):
    clientes = Cliente.objects.all().order_by('dni')
    return render(request, 'cliente_listar.html', {'clientes': clientes})

@login_required
def cliente_agregar(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente agregado correctamente.")
            return redirect('cliente_listar')
        else:
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
        else:
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
>>>>>>> remotes/origin/Rama_Yamil

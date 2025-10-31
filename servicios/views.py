from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Servicio
from .forms import ServicioForm

@login_required
def servicio_listar(request):
    servicios = Servicio.objects.filter(activo=True)
    paginator = Paginator(servicios, 6)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'servicio_listar.html', {'page_obj': page_obj})

@login_required
def servicio_agregar(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            # Acceder al valor desde cleaned_data
            dias_semana = form.cleaned_data['dias_semana']
            cantidad_clases = dias_semana * 4  # Asumiendo 4 semanas por mes

            # Crear instancia pero sin guardar todavía
            servicio = form.save(commit=False)
            servicio.cantidad_clases = cantidad_clases
            servicio.save()

            messages.success(request, "Servicio agregado correctamente.")
            return redirect('servicios:servicio_listar')
        messages.error(request, "Error al guardar. Verificá los datos.")
    else:
        form = ServicioForm()
    return render(request, 'servicio_form.html', {'form': form})


@login_required
def servicio_editar(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio actualizado.")
            return redirect('servicios:servicio_listar')
        messages.error(request, "Error al actualizar. Revisá el formulario.")
    else:
        form = ServicioForm(instance=servicio)
    return render(
        request,
        'servicio_form.html',
        {'form': form, 'servicio': servicio}
    )

@login_required
def servicio_eliminar(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        servicio.soft_delete()
        messages.success(request, "Servicio eliminado.")
        return redirect('servicios:servicio_listar')
    return render(
        request,
        'servicio_eliminar.html',
        {'servicio': servicio}
    )
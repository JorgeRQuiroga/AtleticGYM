from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden
from .forms import UsuarioForm
from django.contrib.auth.models import User as Usuario
from usuarios.forms import EmpleadoForm

# --- Helpers de permisos ---
def es_admin(user):
    return user.groups.filter(name='Administrador').exists()

def es_empleado(user):
    return user.groups.filter(name='Empleado').exists()

# --- Vistas principales ---
@login_required
def home(request):
    return render(request, 'home.html')

# --- Gestión de usuarios ---
@login_required
def usuario_menu(request):
    return render(request, 'usuario_menu.html')

@login_required
def usuario_listar(request):
    buscador = request.GET.get('buscador', '').strip()
    usuarios = Usuario.objects.all().order_by('first_name', 'last_name')

    if buscador:
        usuarios = usuarios.filter(
            Q(first_name__icontains=buscador) |
            Q(last_name__icontains=buscador) |
            Q(email__icontains=buscador) |
            Q(username__icontains=buscador) |
            Q(dni__icontains=buscador) |
            Q(groups__name__icontains=buscador)
        ).distinct()

    paginator = Paginator(usuarios, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'usuario_listar.html', {
        'page_obj': page_obj,
        'buscador': buscador,
    })

@login_required
def usuario_agregar(request):
    if request.method == 'POST':
        u_form = UsuarioForm(request.POST)
        e_form = EmpleadoForm(request.POST)
        if u_form.is_valid() and e_form.is_valid():
            usuario = u_form.save()
            empleado = e_form.save()
            empleado.usuario = usuario
            empleado.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('usuario_listar')
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        e_form = EmpleadoForm()
        u_form = UsuarioForm()
    return render(request, 'usuario_agregar.html', {'u_form': u_form, 'e_form': e_form})

@login_required
def usuario_editar(request, pk):
    if es_empleado(request.user):
        return HttpResponseForbidden("No tenés permisos para editar usuarios.")
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('usuario_listar')
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuario_editar.html', {'form': form, 'usuario': usuario})

@login_required
def usuario_eliminar(request, pk):
    if es_empleado(request.user):
        return HttpResponseForbidden("No tenés permisos para eliminar usuarios.")
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('usuario_listar')
    return render(request, 'usuario_eliminar.html', {'usuario': usuario})
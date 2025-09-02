from django.shortcuts import render

# Create your views here.
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from .forms import UsuarioForm, AsisForm
from .models import Asistencia, Usuario
from clientes.models import Cliente, AsistenciaCliente

def es_admin(user):
    return user.groups.filter(name='Administrador').exists()

def es_empleado(user):
    return user.groups.filter(name='Empleado').exists()

@login_required
def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, 'Inicio de sesión exitoso.')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect('login')

@login_required
def asistencia_listar(request):
    from clientes.models import AsistenciaCliente

    asistencias_usuarios = Asistencia.objects.select_related('usuario')
    asistencias_clientes = AsistenciaCliente.objects.select_related('cliente')

    historial = []

    for a in asistencias_usuarios:
        historial.append({
            'nombre': a.usuario.get_full_name() or a.usuario.username,
            'tipo': 'Usuario',
            'fecha': a.fecha_hora,
        })

    for a in asistencias_clientes:
        historial.append({
            'nombre': a.cliente.nombre,
            'tipo': 'Cliente',
            'fecha': a.fecha_hora,
        })

    historial.sort(key=lambda x: x['fecha'], reverse=True)

    return render(request, 'asistencia_listar.html', {'historial': historial})


def registrar_asistencia(request):
    if request.method == 'POST':
        form = AsisForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            hoy = date.today()

            # Buscar usuario
            usuario = Usuario.objects.filter(dni=dni).first()
            if usuario:
                ya_registrado = Asistencia.objects.filter(usuario=usuario, fecha_hora__date=hoy).exists()
                if ya_registrado:
                    messages.warning(request, f"{usuario.first_name}, ya registraste tu asistencia hoy.")
                else:
                    Asistencia.objects.create(usuario=usuario)
                    messages.success(request, f"¡Bienvenido {usuario.first_name} {usuario.last_name}! Asistencia registrada.")
                return redirect('registrar_asistencia')

            # Buscar cliente
            cliente = Cliente.objects.filter(dni=dni).first()
            if cliente:
                ya_registrado = AsistenciaCliente.objects.filter(cliente=cliente, fecha_hora__date=hoy).exists()
                if ya_registrado:
                    messages.warning(request, f"{cliente.nombre}, ya registraste tu asistencia hoy.")
                else:
                    AsistenciaCliente.objects.create(cliente=cliente)
                    messages.success(request, f"¡Bienvenido {cliente.nombre}! Asistencia registrada.")
                return redirect('registrar_asistencia')

            messages.error(request, "No se encontró ningún usuario o cliente con ese DNI.")
            return redirect('registrar_asistencia')
    else:
        form = AsisForm()

    return render(request, 'registrar_asistencia.html', {'form': form})

@login_required
def usuario_listar(request):
    usuarios = Usuario.objects.all().order_by('first_name', 'last_name')

    nombre = request.GET.get('nombre')
    correo = request.GET.get('correo')
    grupo = request.GET.get('grupo')

    if nombre:
        usuarios = usuarios.filter(first_name__icontains=nombre)
    if correo:
        usuarios = usuarios.filter(email__icontains=correo)
    if grupo:
        usuarios = usuarios.filter(groups__name=grupo)

    return render(request, 'usuario_listar.html', {'usuarios': usuarios})

@login_required
def usuario_agregar(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('usuario_listar')
        else:
            messages.error(request, 'Por favor, corrige los errores del formulario.')
    else:
        form = UsuarioForm()
    return render(request, 'usuario_agregar.html', {'form': form})

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
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistroAsistenciaForm
from .models import Asistencia
from membresias.models import Membresia
from empleados.models import Empleado
from django.utils import timezone

@login_required
def registrar_asistencia(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        dni = request.POST.get('dni')
        registrado_por = request.user
        hoy = timezone.now().date()
        if tipo == 'alumno':
            membresia = Membresia.objects.filter(cliente__dni=dni, activa=True).first()
            if not membresia:
                messages.error(request, "No se encontró una membresía activa para ese DNI.")
            else:
                # Verificar si ya existe asistencia hoy
                existe = Asistencia.objects.filter(
                    tipo='alumno',
                    membresia=membresia,
                    fecha_hora__date=hoy
                ).exists()

                if existe:
                    messages.warning(request, f"Ya existe una asistencia registrada hoy para {membresia.cliente}.")
                else:
                    Asistencia.objects.create(
                        tipo='alumno',
                        membresia=membresia,
                        registrado_por=registrado_por
                    )
                    messages.success(request, f"Asistencia registrada para {membresia.cliente}.")
        elif tipo == 'empleado':
            empleado = Empleado.objects.filter(dni=dni).first()
            if not empleado:
                messages.error(request, "No se encontró un empleado con ese DNI.")
            else:
                # Verificar si ya existe asistencia hoy
                existe = Asistencia.objects.filter(
                    tipo='empleado',
                    empleado=empleado,
                    fecha_hora__date=hoy
                ).exists()

                if existe:
                    messages.warning(request, f"Ya existe una asistencia registrada hoy para {empleado}.")
                else:
                    Asistencia.objects.create(
                        tipo='empleado',
                        empleado=empleado,
                        registrado_por=registrado_por
                    )
                    messages.success(request, f"Asistencia registrada para {empleado}.")

        return redirect('asistencias:asistencia_opciones')

    return render(request, 'asistencia_opciones.html')

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from clientes.models import Cliente
from empleados.models import Empleado
from membresias.models import Membresia
from asistencias.models import Asistencia
from .forms import AsistenciaForm


@login_required
def asistencia_form(request, tipo, pk):
    """
    Devuelve el formulario de asistencia para cliente o empleado en un modal.
    """
    if tipo == "cliente":
        objeto = get_object_or_404(Cliente, pk=pk)
    else:
        objeto = get_object_or_404(Empleado, pk=pk)

    form = AsistenciaForm(initial={'tipo': tipo})
    html_form = render_to_string(
        'asistencia_form.html',
        {'form': form, 'objeto': objeto, 'tipo': tipo},
        request=request
    )
    return JsonResponse({'html_form': html_form})


@login_required
@require_POST
def asistencia_guardar(request, tipo, pk):
    """
    Procesa el guardado de asistencia desde el modal.
    """
    if tipo == "cliente":
        cliente = get_object_or_404(Cliente, pk=pk)
        membresia = Membresia.objects.filter(
            cliente=cliente, activa=True, fecha_fin__gte=timezone.now().date()
        ).first()
        if not membresia:
            return JsonResponse({
                'success': False,
                'error': f"El cliente {cliente.nombre} no tiene membresía activa."
            })

        asistencia = Asistencia.objects.create(
            tipo='cliente',
            cliente=cliente,
            membresia=membresia,
            fecha_hora=timezone.now(),
            registrado_por=request.user
        )
        return JsonResponse({'success': True})

    elif tipo == "empleado":
        empleado = get_object_or_404(Empleado, pk=pk)
        asistencia = Asistencia.objects.create(
            tipo='empleado',
            empleado=empleado,
            fecha_hora=timezone.now(),
            registrado_por=request.user
        )
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Tipo no válido'})
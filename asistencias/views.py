from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
from .models import Asistencia
from membresias.models import Membresia

@login_required
def asistencia_opciones(request):
    """
    Vista que simplemente renderiza la página del menú de opciones de asistencia.
    """
    return render(request, 'asistencia_opciones.html')

class RegistrarAsistenciaView(View):
    """
    Gestiona la pantalla de "modo kiosco" para que los clientes registren su asistencia.
    No requiere que el usuario esté logueado.
    """
    template_name = 'asistencia_registrar.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        dni = request.POST.get('dni', '').strip()
        if not dni.isdigit():
            messages.error(request, 'Por favor, ingrese un DNI válido (solo números).')
            return render(request, self.template_name)

        try:
            membresia = Membresia.objects.select_related('cliente', 'servicio').get(cliente__dni=dni, activa=True)
        except Membresia.DoesNotExist:
            messages.error(request, f'No se encontró una membresía activa para el DNI {dni}. Por favor, acérquese a recepción.')
            return render(request, self.template_name)

        if membresia.fecha_fin < timezone.now().date():
            messages.warning(request, f'Hola {membresia.cliente.nombre}, tu membresía ha vencido. Por favor, acércate a recepción.')
            return render(request, self.template_name, {'membresia': membresia})

        if membresia.servicio.cantidad_clases > 0 and membresia.clases_restantes <= 0:
            messages.warning(request, f'Hola {membresia.cliente.nombre}, no te quedan clases disponibles. Por favor, acércate a recepción.')
            return render(request, self.template_name, {'membresia': membresia})

        Asistencia.objects.create(membresia=membresia)
        
        if membresia.servicio.cantidad_clases > 0:
            membresia.clases_restantes -= 1
            membresia.save()

        return render(request, self.template_name, {'membresia': membresia})

@login_required
def lista_asistencias(request):
    asistencias = Asistencia.objects.select_related('membresia__cliente', 'membresia__servicio').order_by('-fecha_hora')[:100]
    return render(request, 'asistencia_lista.html', {'asistencias': asistencias})

def grafico_asistencias(request):
    return render(request, 'grafico_asistencias.html')
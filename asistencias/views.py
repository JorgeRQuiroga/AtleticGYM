from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
from .models import Asistencia
from membresias.models import Membresia
from datetime import timedelta

@login_required
def asistencia_opciones(request):
    # Vista que simplemente renderiza la página del menú de opciones de asistencia.
    return render(request, 'asistencia_opciones.html')

class RegistrarAsistenciaView(View):
    template_name = 'asistencia_registrar.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        dni = request.POST.get('dni', '').strip()
        if not dni.isdigit():
            messages.error(request, 'Por favor, ingrese un DNI válido (solo números).')
            return render(request, self.template_name)

        try:
            membresia = Membresia.objects.select_related('cliente', 'servicio').get(
                cliente__dni=dni, activa=True
            )
        except Membresia.DoesNotExist:
            messages.error(request, f'No se encontró una membresía activa para el DNI {dni}.')
            return render(request, self.template_name)

        hoy = timezone.now().date()

        # 1. Verificar fecha de vencimiento
        if membresia.fecha_fin < hoy:
            messages.warning(request, f'Hola {membresia.cliente.nombre}, tu membresía ha vencido.')
            return render(request, self.template_name, {'membresia': membresia})

        # 2. Verificar clases restantes
        if membresia.servicio.cantidad_clases > 0 and membresia.clases_restantes <= 0:
            messages.warning(request, f'Hola {membresia.cliente.nombre}, no te quedan clases disponibles.')
            return render(request, self.template_name, {'membresia': membresia})

        # 3. Verificar límite semanal
        # asumimos que tu modelo Servicio tiene un campo `veces_por_semana`
        if hasattr(membresia.servicio, 'veces_por_semana') and membresia.servicio.veces_por_semana:
            inicio_semana = hoy - timedelta(days=hoy.weekday())  # lunes
            fin_semana = inicio_semana + timedelta(days=6)       # domingo

            usadas_esta_semana = membresia.asistencias.filter(
                fecha__range=(inicio_semana, fin_semana)
            ).count()

            if usadas_esta_semana >= membresia.servicio.veces_por_semana:
                messages.warning(
                    request,
                    f'Hola {membresia.cliente.nombre}, ya alcanzaste tu límite semanal '
                    f'de {membresia.servicio.veces_por_semana} asistencias.'
                )
                return render(request, self.template_name, {'membresia': membresia})

        # 4. Registrar asistencia
        Asistencia.objects.create(membresia=membresia)

        if membresia.servicio.cantidad_clases > 0:
            membresia.clases_restantes -= 1
            membresia.save()

        return render(request, self.template_name, {'membresia': membresia})

@login_required
def lista_asistencias(request):
    asistencias = Asistencia.objects.select_related('membresia__cliente', 'membresia__servicio').order_by('-fecha_hora')[:100]
    return render(request, 'asistencia_lista.html', {'asistencias': asistencias})

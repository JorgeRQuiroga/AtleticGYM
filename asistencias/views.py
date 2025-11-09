from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils import timezone
from .models import Asistencia
from membresias.models import Membresia
#graficos---
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractWeekDay, ExtractHour

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
    # Fecha actual para filtrar el año
    hoy = timezone.now()
    año_actual = hoy.year

    # --- Gráfico 1: Asistencias por mes ---
    asistencias_mes = (
        Asistencia.objects.filter(fecha_hora__year=año_actual)
        .annotate(mes=ExtractMonth('fecha_hora'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    meses = [r['mes'] for r in asistencias_mes]
    totales_mes = [r['total'] for r in asistencias_mes]

    # --- Gráfico 2: Asistencias por día de la semana ---
    # Django: domingo=1 ... sábado=7
    asistencias_dia = (
        Asistencia.objects
        .annotate(dia=ExtractWeekDay('fecha_hora'))
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('dia')
    )

    dias_semana_labels = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
    totales_dia = [0] * 7
    for r in asistencias_dia:
        totales_dia[r['dia'] - 1] = r['total']

    # --- Gráfico 3: Asistencias por hora ---
    asistencias_hora = (
        Asistencia.objects
        .annotate(hora=ExtractHour('fecha_hora'))
        .values('hora')
        .annotate(total=Count('id'))
        .order_by('hora')
    )

    horas = [r['hora'] for r in asistencias_hora]
    totales_hora = [r['total'] for r in asistencias_hora]

    contexto = {
        'meses': meses,
        'totales_mes': totales_mes,
        'dias_semana_labels': dias_semana_labels,
        'totales_dia': totales_dia,
        'horas': horas,
        'totales_hora': totales_hora,
    }
    return render(request, 'grafico_asistencias.html', contexto)
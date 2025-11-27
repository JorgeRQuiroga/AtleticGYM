from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from asistencias.models import Asistencia
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractWeekDay, ExtractHour
from membresias.models import Membresia
from django.db.models.functions import TruncMonth
from datetime import date, timedelta
import calendar
from cajas.models import Caja
from django.db.models import Sum


# Vista menú principal
def menu_graficos(request):
    return render(request, "graficos_menu.html")

def grafico_asistencias(request):
    # Año fijo 2025 (o poné año_actual si querés que sea dinámico)
    año_actual = 2025  

    # --- Gráfico 1: Asistencias por mes ---
    asistencias_mes = (
        Asistencia.objects.filter(fecha_hora__year=año_actual)
        .annotate(mes=ExtractMonth('fecha_hora'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    # Lista de meses del 1 al 12
    meses = [        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


    # Inicializar totales en 0
    totales_mes = [0] * 12

    # Cargar los datos reales
    for r in asistencias_mes:
        totales_mes[r['mes'] - 1] = r['total']

    # --- Gráfico 2: Asistencias por día ---
    asistencias_dia = (
        Asistencia.objects
        .annotate(dia=ExtractWeekDay('fecha_hora'))
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('dia')
    )

    dias_semana_labels = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
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

    # Lista de horas 0–23
    horas = list(range(24))
    totales_hora = [0] * 24

    for r in asistencias_hora:
        totales_hora[r['hora']] = r['total']

    contexto = {
        'meses': meses,
        'totales_mes': totales_mes,
        'dias_semana_labels': dias_semana_labels,
        'totales_dia': totales_dia,
        'horas': horas,
        'totales_hora': totales_hora,
    }

    return render(request, 'graficos_asistencia.html', contexto)


###

def grafico_membresias(request):

    # === Distribución de membresías activas ===
    distribucion = (
        Membresia.objects
        .filter(activa=True)
        .values('servicio__nombre')
        .annotate(total=Count('id'))
        .order_by('servicio__nombre')
    )

    labels_membresias = [d['servicio__nombre'] for d in distribucion]
    data_membresias = [d['total'] for d in distribucion]

    # === Altas últimos 12 meses ===
    hoy = date.today()
    año_actual = hoy.year
    mes_actual = hoy.month

    meses_labels = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    altas_data = [0] * 12

    altas = (
        Membresia.objects
        .filter(
            fecha_inicio__gte=hoy.replace(year=hoy.year - 1),
            fecha_inicio__lte=hoy
        )
        .annotate(mes=ExtractMonth('fecha_inicio'))
        .values('mes')
        .annotate(total=Count('id'))
    )

    for a in altas:
        idx = a['mes'] - 1
        altas_data[idx] = a['total']

    context = {
        'labels_membresias': labels_membresias,
        'data_membresias': data_membresias,
        'meses': meses_labels,
        'altas_data': altas_data,
    }

    return render(request, 'graficos_membresias.html', context)

###


def grafico_ingresos(request):
    hoy = date.today()

    # ============================================================
    # 1) INGRESOS POR DÍA DE LA SEMANA (LUN → DOM)
    # Últimos 30 días
    # ============================================================
    hace_30_dias = hoy - timedelta(days=30)

    registros = (
        Caja.objects
        .filter(fecha_apertura__gte=hace_30_dias)
        .values('fecha_apertura')
        .annotate(total=Sum('monto_cierre'))
    )

    # Días en español
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    # Inicializo con 0 los 7 días
    ingresos_por_dia = {i: 0 for i in range(7)}  # lunes=0 ... domingo=6

    for r in registros:
        dia = r['fecha_apertura'].weekday()  # lunes=0 ... domingo=6
        ingresos_por_dia[dia] += float(r['total']) if r['total'] else 0

    labels_semanales = dias_semana
    data_semanales = [ingresos_por_dia[i] for i in range(7)]

    # ============================================================
    # 2) INGRESOS POR MES DEL AÑO ACTUAL (ENE → DIC)
    # ============================================================
    año_actual = hoy.year

    registros_mensuales = (
        Caja.objects
        .filter(fecha_apertura__year=año_actual)
        .values('fecha_apertura__month')
        .annotate(total=Sum('monto_cierre'))
    )

    # Meses en español
    meses_es = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    ingresos_por_mes = {m: 0 for m in range(1, 13)}

    for r in registros_mensuales:
        mes = r['fecha_apertura__month']
        ingresos_por_mes[mes] += float(r['total']) if r['total'] else 0

    labels_anuales = meses_es
    data_anuales = [ingresos_por_mes[m] for m in range(1, 13)]

    # ============================================================
    # CONTEXTO
    # ============================================================
    context = {
        'labels_semanales': labels_semanales,
        'data_semanales': data_semanales,
        'labels_anuales': labels_anuales,
        'data_anuales': data_anuales,
        'anio': año_actual,
    }

    return render(request, 'graficos_ingresos.html', context)




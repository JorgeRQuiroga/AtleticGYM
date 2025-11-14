from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from asistencias.models import Asistencia
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractWeekDay, ExtractHour

# Vista menú principal
def menu_graficos(request):
    return render(request, "graficos_menu.html")

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
    return render(request, 'graficos_asistencia.html', contexto)

from membresias.models import Membresia
from django.db.models.functions import TruncMonth
from datetime import date, timedelta

def grafico_membresias(request):
    # --- 1. Distribución de membresías activas ---
    distribucion = (
        Membresia.objects
        .filter(activa=True)
        .values('servicio__nombre')
        .annotate(total=Count('id'))
        .order_by('servicio__nombre')
    )
    labels_membresias = [d['servicio__nombre'] for d in distribucion]
    data_membresias = [d['total'] for d in distribucion]
 
    # --- 2. Altas vs Bajas mensuales últimos 12 meses ---
    hoy = date.today()
    hace_un_anio = hoy - timedelta(days=365)
 
    # Altas por mes
    altas = (
        Membresia.objects
        .filter(fecha_inicio__gte=hace_un_anio)
        .annotate(mes=TruncMonth('fecha_inicio'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
 
    # Bajas por mes (cuando se desactivan)
    bajas = (
        Membresia.objects
        .filter(activa=False, fecha_fin__gte=hace_un_anio)
        .annotate(mes=TruncMonth('fecha_fin'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    meses = [a['mes'].strftime("%b %Y") for a in altas]
    altas_data = [a['total'] for a in altas]
    bajas_data = [b['total'] for b in bajas]
    
    # --- Combinación de datos para alinear meses ---
    # Creamos un diccionario para cada mes de los últimos 12
    meses_dict = {}
    for i in range(12):
        mes_actual = (hoy.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        meses_dict[mes_actual.strftime('%Y-%m')] = {'altas': 0, 'bajas': 0}

    # Llenamos con los datos de altas
    for alta in altas:
        mes_key = alta['mes'].strftime('%Y-%m')
        if mes_key in meses_dict:
            meses_dict[mes_key]['altas'] = alta['total']

    # Llenamos con los datos de bajas
    for baja in bajas:
        mes_key = baja['mes'].strftime('%Y-%m')
        if mes_key in meses_dict:
            meses_dict[mes_key]['bajas'] = baja['total']

    meses_ordenados = sorted(meses_dict.keys())
    # Render
    context = {
        'labels_membresias': labels_membresias,
        'data_membresias': data_membresias,
        'meses': meses,
        'altas_data': altas_data,
        'bajas_data': bajas_data,
        'meses': [date.fromisoformat(m + '-01').strftime('%b %Y') for m in meses_ordenados],
        'altas_data': [meses_dict[m]['altas'] for m in meses_ordenados],
        'bajas_data': [meses_dict[m]['bajas'] for m in meses_ordenados],

    }
    return render(request, 'graficos_membresias.html', context)



from django.db.models import Sum
from django.db.models.functions import TruncWeek, TruncMonth
from datetime import date, timedelta
from cajas.models import Caja

def grafico_ingresos(request):
    hoy = date.today()
    hace_un_anio = hoy - timedelta(days=365)

    # --- 1. Ingresos semanales (últimas 8 semanas) ---
    ingresos_semanales = (
        Caja.objects
        .filter(fecha_apertura__gte=hoy - timedelta(weeks=8))
        .annotate(semana=TruncWeek('fecha_apertura'))
        .values('semana')
        .annotate(total=Sum('monto_cierre'))
        .order_by('semana')
    )

    labels_semanales = [i['semana'].strftime('%d %b') for i in ingresos_semanales]
    data_semanales = [float(i['total']) if i['total'] else 0 for i in ingresos_semanales]

    # --- 2. Ingresos anuales (últimos 12 meses) ---
    ingresos_anuales = (
        Caja.objects
        .filter(fecha_apertura__gte=hace_un_anio)
        .annotate(mes=TruncMonth('fecha_apertura'))
        .values('mes')
        .annotate(total=Sum('monto_cierre'))
        .order_by('mes')
    )

    labels_anuales = [i['mes'].strftime('%b %Y') for i in ingresos_anuales]
    data_anuales = [float(i['total']) if i['total'] else 0 for i in ingresos_anuales]

    context = {
        'labels_semanales': labels_semanales,
        'data_semanales': data_semanales,
        'labels_anuales': labels_anuales,
        'data_anuales': data_anuales,
    }

    return render(request, 'graficos_ingresos.html', context)

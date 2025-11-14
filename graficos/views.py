from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from asistencias.models import Asistencia

# Vista menú principal
def menu_graficos(request):
    return render(request, "graficos_menu.html")

# Vista HTML del gráfico de asistencias
def grafico_asistencias(request):
    return render(request, "graficos_asistencias.html")

# Endpoint de datos para Chart.js
def datos_asistencias(request):
    periodo = request.GET.get("periodo", "semana")  # semana, mes, año
    hoy = timezone.now().date()

    qs = Asistencia.objects.all()

    qs = Asistencia.objects.all()

    if periodo == "semana":
        qs = qs.filter(fecha_hora__week=hoy.isocalendar()[1], fecha_hora__year=hoy.year)
    elif periodo == "mes":
        qs = qs.filter(fecha_hora__month=hoy.month, fecha_hora__year=hoy.year)
    elif periodo == "año":
        qs = qs.filter(fecha_hora__year=hoy.year)


    # Agrupar por hora
    data = {}
    for asistencia in qs:
        hora = asistencia.fecha_hora.hour
        data[hora] = data.get(hora, 0) + 1


    # Ordenar por hora
    horas = sorted(data.keys())
    valores = [data[h] for h in horas]

    return JsonResponse({
        "labels": [f"{h:02d}:00" for h in horas],
        "values": valores
    })

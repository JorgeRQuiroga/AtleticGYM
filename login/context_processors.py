def grupos_usuario(request):
    es_duenio = False
    es_empleado = False

    if request.user.is_authenticated:
        es_duenio = request.user.groups.filter(name="Duenio").exists()
        es_empleado = request.user.groups.filter(name="Empleado").exists()

    return {
        "es_duenio": es_duenio,
        "es_empleado": es_empleado,
    }

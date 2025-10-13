# admin.py
from django.contrib import admin
from .models import Servicio

class ServicioAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'cantidad', 'precio', 'estado')
    list_editable = ('cantidad', 'precio', 'estado')
    list_filter   = ('estado',)
    search_fields = ('nombre',)
    ordering      = ('nombre',)

admin.site.register(Servicio, ServicioAdmin)
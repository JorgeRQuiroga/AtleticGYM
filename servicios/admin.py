# admin.py
from django.contrib import admin
from .models import Servicio

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'cantidad_clases', 'precio', 'activo')
    list_filter = ('activo',)
    list_editable = ('cantidad_clases', 'precio', 'activo')
    search_fields = ('nombre',)
    ordering = ('nombre',)



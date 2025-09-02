from django.contrib import admin
from .models import Cliente

class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'dni', 'telefono', 'email']
    search_fields = ['nombre', 'apellido', 'dni', 'email']
    list_filter = ['telefono']
    ordering = ['apellido', 'nombre']

admin.site.register(Cliente, ClienteAdmin)

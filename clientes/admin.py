from django.contrib import admin
<<<<<<< HEAD

# Register your models here.
=======
from .models import Cliente

class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'dni', 'telefono', 'email']
    search_fields = ['nombre', 'apellido', 'dni', 'email']
    list_filter = ['telefono']
    ordering = ['apellido', 'nombre']

admin.site.register(Cliente, ClienteAdmin)
>>>>>>> remotes/origin/Rama_Yamil

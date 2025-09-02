from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
class CustomUsuarioAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name' ,'dni',]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name','dni', 'telefono', 'email', )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = ((None, {'fields':('username','first_name', 'last_name','dni','telefono', 'email', 'password1', 'password2')}),)

admin.site.register(Usuario, CustomUsuarioAdmin)
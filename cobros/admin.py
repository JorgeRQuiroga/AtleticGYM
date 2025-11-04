from django.contrib import admin
from .models import Cobro, DetalleCobro, MetodoDePago
# Register your models here.

admin.site.register(Cobro)
admin.site.register(DetalleCobro)
admin.site.register(MetodoDePago)
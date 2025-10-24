from django import forms
from django.contrib.auth.models import User
from .models import Empleado
from datetime import date

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['dni', 'nombre', 'apellido', 'telefono', 'domicilio']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if self.instance.pk:
            # Si estamos editando, excluir el propio empleado de la búsqueda
            if Empleado.objects.filter(dni=dni).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ya existe un empleado con este DNI")
        return dni
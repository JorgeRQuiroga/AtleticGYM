from django import forms
from .models import Empleado

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['dni', 'nombre', 'apellido', 'telefono', 'domicilio']
        widgets = {
            'dni': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese DNI'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese apellido'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese teléfono'
            }),
            'domicilio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese domicilio'
            }),
        }

    def clean_dni(self):
        dni = self.cleaned_data['dni']
        if self.instance.pk:
            # Si estamos editando, excluir el propio empleado de la búsqueda
            if Empleado.objects.filter(dni=dni).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ya existe un empleado con este DNI")
        else:
            # Si es un alta nueva, validar que no exista
            if Empleado.objects.filter(dni=dni).exists():
                raise forms.ValidationError("Ya existe un empleado con este DNI")
        return dni
import re
from django import forms
from .models import Empleado


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['dni', 'nombre', 'apellido', 'telefono', 'domicilio']
        widgets = {
            'dni': forms.TextInput(attrs={
                'class': 'form-control bg-transparent text-white',
                'placeholder': 'Ingrese DNI'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control bg-transparent text-white',
                'placeholder': 'Ingrese nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control bg-transparent text-white',
                'placeholder': 'Ingrese apellido'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control bg-transparent text-white',
                'placeholder': 'Ingrese teléfono'
            }),
            'domicilio': forms.Textarea(attrs={
                'class': 'form-control bg-transparent text-white',
                'rows': 3,
                'placeholder': 'Ingrese domicilio'
            }),
        }

    def clean_dni(self):
        dni = (self.cleaned_data.get('dni') or '').strip()
        if not dni.isdigit():
            raise forms.ValidationError("El DNI solo puede contener números.")
        return dni

    def validate_unique(self):
        # Evita que el ModelForm ejecute las validaciones de unique del modelo.
        # La vista ya se encarga de la unicidad, por eso aquí no hacemos nada.
        return


    def clean_nombre(self):
        nombre = (self.cleaned_data.get('nombre') or '').strip()
        # Solo letras y espacios
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', nombre):
            raise forms.ValidationError("El nombre solo puede contener letras.")
        return nombre.title()

    def clean_apellido(self):
        apellido = (self.cleaned_data.get('apellido') or '').strip()
        # Solo letras y espacios
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', apellido):
            raise forms.ValidationError("El apellido solo puede contener letras.")
        return apellido.title()

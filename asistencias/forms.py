from django import forms
from django.core.exceptions import ValidationError
from .models import Empleado


class AsistenciaForm(forms.Form):
    dni = forms.IntegerField(
        label="Ingrese su DNI",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 30111222',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
        })
    )
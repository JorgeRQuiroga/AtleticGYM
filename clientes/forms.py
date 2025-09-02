from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'dni', 'telefono', 'emergencia', 'email']
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'dni': 'DNI',
            'telefono': 'Teléfono',
            'emergencia': 'Teléfono de Emergencia',
            'email': 'Correo Electrónico',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pérez'}),
            'dni': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 30111222'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3874123456'}),
            'emergencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3874000000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej: juan@example.com'}),
        }
from django import forms
from .models import Cliente
from servicios.models import Servicio

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellido', 'dni', 'telefono', 'emergencia', 'email',
            'servicio', 'membresia_activa'
        ]
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'dni': 'DNI',
            'telefono': 'Teléfono',
            'emergencia': 'Teléfono de Emergencia',
            'email': 'Correo Electrónico',
            'servicio': 'Servicio (solo activos)',
            'membresia_activa': 'Membresía activa'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pérez'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 30111222'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3874123456'}),
            'emergencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3874000000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej: juan@example.com'}),
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'membresia_activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo servicios activos ordenados por nombre
        self.fields['servicio'].queryset = Servicio.objects.filter(estado=True).order_by('nombre')
        self.fields['servicio'].required = False
        self.fields['email'].required = False

    def clean(self):
        cleaned = super().clean()
        servicio = cleaned.get('servicio')
        membresia_activa = cleaned.get('membresia_activa')

        # Evitar activar membresía si el servicio está inactivo (por seguridad)
        if servicio and not servicio.estado and membresia_activa:
            self.add_error('membresia_activa', 'No se puede activar la membresía con un servicio inactivo.')

        return cleaned
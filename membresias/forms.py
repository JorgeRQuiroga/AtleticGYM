from django import forms
from clientes.models import Cliente
from servicios.models import Servicio
from .models import Membresia
from django.utils import timezone
from datetime import timedelta


class MembresiaInscripcionForm(forms.ModelForm):
    # Campos de Cliente
    nombre = forms.CharField(
        required=True,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    apellido = forms.CharField(
        required=True,
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )
    dni = forms.CharField(
        required=True,
        label="DNI",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Documento de identidad'})
    )
    telefono = forms.CharField(
        required=True,
        label="Teléfono",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono principal'})
    )
    emergencia = forms.CharField(
        required=False,
        label="Teléfono de emergencia",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono de emergencia'})
    )
    domicilio = forms.CharField(
        required=False,
        label="Domicilio",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'})
    )
    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )

    # Campo de Servicio
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True),
        required=True,
        label="Servicio",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Membresia
        fields = ['servicio']

    def save(self, commit=True):
        # Crear cliente
        cliente = Cliente.objects.create(
            nombre=self.cleaned_data['nombre'],
            apellido=self.cleaned_data['apellido'],
            dni=self.cleaned_data['dni'],
            telefono=self.cleaned_data['telefono'],
            emergencia=self.cleaned_data.get('emergencia'),
            domicilio=self.cleaned_data.get('domicilio'),
            email=self.cleaned_data.get('email'),
        )

        # Tomar el servicio seleccionado
        servicio = self.cleaned_data['servicio']

        # Calcular fecha de fin automáticamente
        hoy = timezone.now().date()
        dias_a_sumar = getattr(servicio, 'cantidad_clases', 0)
        fecha_fin = hoy + timedelta(days=dias_a_sumar)

        # Crear membresía
        membresia = Membresia.objects.create(
            cliente=cliente,
            servicio=servicio,
            fecha_fin=fecha_fin,
            clases_restantes=dias_a_sumar,
            activa=True
        )
        return membresia

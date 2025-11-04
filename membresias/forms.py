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
        queryset=Servicio.objects.filter(activo=True).exclude(nombre__icontains='Por clase'),
        required=True,
        label="Servicio",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    observaciones = forms.CharField(
        required=False,
        label = "Observaciones",
        widget = forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Observaciones adicionales'})
    )

    class Meta:
        model = Membresia
        fields = ['servicio', 'observaciones']

    def __init__(self, *args, **kwargs):
        # Capturamos el argumento extra
        self.membresia_instance = kwargs.pop('membresia_instance', None)
        super().__init__(*args, **kwargs)

        if self.membresia_instance:
            c = self.membresia_instance.cliente
            # precargar datos del cliente
            self.fields['nombre'].initial = c.nombre
            self.fields['apellido'].initial = c.apellido
            self.fields['dni'].initial = c.dni
            self.fields['telefono'].initial = c.telefono
            self.fields['emergencia'].initial = c.emergencia
            self.fields['domicilio'].initial = c.domicilio
            self.fields['email'].initial = c.email
            # precargar datos de la membresía
            self.fields['servicio'].initial = self.membresia_instance.servicio
            self.fields['observaciones'].initial = self.membresia_instance.observaciones

    def save(self, commit=True):
        servicio = self.cleaned_data['servicio']
        observaciones = self.cleaned_data.get('observaciones', '')

        if self.membresia_instance:
            # --- MODO EDICIÓN ---
            cliente = self.membresia_instance.cliente
            cliente.nombre = self.cleaned_data['nombre']
            cliente.apellido = self.cleaned_data['apellido']
            cliente.dni = self.cleaned_data['dni']
            cliente.telefono = self.cleaned_data['telefono']
            cliente.emergencia = self.cleaned_data.get('emergencia')
            cliente.domicilio = self.cleaned_data.get('domicilio')
            cliente.email = self.cleaned_data.get('email')
            if commit:
                cliente.save()

            membresia = self.membresia_instance
            membresia.servicio = servicio
            membresia.observaciones = observaciones
            if commit:
                membresia.save()
            return membresia

        # --- MODO CREACIÓN ---
        cliente = Cliente.objects.create(
            nombre=self.cleaned_data['nombre'],
            apellido=self.cleaned_data['apellido'],
            dni=self.cleaned_data['dni'],
            telefono=self.cleaned_data['telefono'],
            emergencia=self.cleaned_data.get('emergencia'),
            domicilio=self.cleaned_data.get('domicilio'),
            email=self.cleaned_data.get('email'),
        )

        hoy = timezone.now().date()
        fecha_fin = hoy + timedelta(days=30)
        clases = getattr(servicio, 'cantidad_clases', 0)

        membresia = Membresia.objects.create(
            cliente=cliente,
            servicio=servicio,
            fecha_fin=fecha_fin,
            clases_restantes=clases,
            activa=True,
            observaciones=observaciones
        )
        return membresia
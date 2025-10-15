from django import forms
from clientes.models import Cliente
from servicios.models import Servicio
from .models import Membresia

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
        required=False, 
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

    cantidad_clases = forms.IntegerField(
        required=False, 
        label="Cantidad de clases", 
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad de clases'})
    )

    fecha_fin = forms.DateField(
        required=False,
        label="Fecha de fin",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    activa = forms.BooleanField(
        required=False,
        label="Membresía activa",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Membresia
        fields = ['servicio', 'fecha_fin', 'activa']

    def save(self, commit=True):
        # Crear cliente
        cliente = Cliente.objects.create(
            nombre=self.cleaned_data['nombre'],
            apellido=self.cleaned_data['apellido'],
            dni=self.cleaned_data['dni'],
            telefono=self.cleaned_data['telefono'],
            emergencia=self.cleaned_data.get('telefono_emergencia'),
            domicilio=self.cleaned_data.get('domicilio'),
            email=self.cleaned_data.get('email'),
        )
        # Crear membresía
        membresia = Membresia.objects.create(
            cliente=cliente,
            servicio=self.cleaned_data['servicio'],
            fecha_fin=self.cleaned_data.get('fecha_fin'),
            clases_restantes=self.cleaned_data.get('cantidad_clases', 0),
            activa=self.cleaned_data['activa']
        )
        return membresia

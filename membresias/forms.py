from django import forms
from clientes.models import Cliente
from servicios.models import Servicio
from .models import Membresia
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
import re
from cobros.models import MetodoDePago

class MembresiaInscripcionForm(forms.ModelForm):
    # Campos de Cliente
    nombre = forms.CharField(
        required=True, label="Nombre *",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white', 'placeholder': 'Nombre'})
    )
    apellido = forms.CharField(
        required=True, label="Apellido *",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white', 'placeholder': 'Apellido'})
    )
    dni = forms.CharField(
        required=True, label="DNI *",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white', 'placeholder': 'Documento de identidad'})
    )
    telefono = forms.CharField(
        required=True, label="Teléfono *",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white', 'placeholder': 'Teléfono principal'})
    )
    emergencia = forms.CharField(
        required=False, label="Teléfono de emergencia",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white', 'placeholder': 'Teléfono de emergencia'})
    )
    domicilio = forms.CharField(
        required=False, label="Domicilio",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white', 'placeholder': 'Dirección'})
    )
    email = forms.EmailField(
        required=False, label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control bg-transparent text-white', 'placeholder': 'Correo electrónico'})
    )

    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True).exclude(nombre__icontains='Por clase'),
        required=True, label="Servicio *",
        widget=forms.Select(attrs={'class': 'form-select bg-transparent text-white'})
    )
    observaciones = forms.CharField(
        required=False, label="Observaciones",
        widget=forms.Textarea(attrs={'class': 'form-control bg-transparent text-white', 'placeholder': 'Observaciones adicionales'})
    )
    metodo_pago = forms.ModelChoiceField(
        required=True,
        queryset=MetodoDePago.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select bg-transparent text-white'}),
        label="Método de Pago *"
    )

    class Meta:
        model = Membresia
        fields = ['servicio', 'observaciones', 'metodo_pago']
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', nombre):
            raise ValidationError("El nombre solo puede contener letras y espacios.")
        return nombre.title()

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido', '').strip()
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', apellido):
            raise ValidationError("El apellido solo puede contener letras y espacios.")
        return apellido.title()

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '').strip()
        if not dni.isdigit():
            raise ValidationError("El DNI debe contener solo números.")
        if len(dni) < 7 or len(dni) > 8:
            raise ValidationError("El DNI debe tener entre 7 y 8 dígitos.")
        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
        if not re.match(r'^\+?[0-9]{8,15}$', telefono_limpio):
            raise ValidationError("Ingrese un número de teléfono válido (mínimo 8 dígitos).")
        return telefono

    def clean_emergencia(self):
        emergencia = (self.cleaned_data.get('emergencia') or '').strip()
        # Si está vacío, lo devolvemos directamente
        if not emergencia:
            return emergencia

    # Si tiene contenido, validamos formato
        emergencia_limpio = re.sub(r'[\s\-\(\)]', '', emergencia)
        if not re.match(r'^\+?[0-9]{8,15}$', emergencia_limpio):
            raise ValidationError("Ingrese un número de emergencia válido (mínimo 8 dígitos).")
        return emergencia


    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        # Si está vacío, lo devolvemos directamente
        if not email:
            return email

        # Si tiene contenido, validamos formato
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Ingrese un email válido.")
        return email
    
    def save(self, commit=True):
            servicio = self.cleaned_data['servicio']
            observaciones = self.cleaned_data.get('observaciones', '')
            dni_ingresado = self.cleaned_data['dni']

            # Lógica principal: Buscar si existe, o crear uno nuevo
            # get_or_create devuelve una tupla (objeto, creado_boolean)
            cliente, created = Cliente.objects.get_or_create(dni=dni_ingresado)

            # Independientemente de si es nuevo o viejo (de la clase de prueba),
            # ACTUALIZAMOS sus datos con la información real del formulario.
            cliente.nombre = self.cleaned_data['nombre']
            cliente.apellido = self.cleaned_data['apellido']
            cliente.telefono = self.cleaned_data['telefono']
            cliente.emergencia = self.cleaned_data.get('emergencia')
            cliente.domicilio = self.cleaned_data.get('domicilio')
            cliente.email = self.cleaned_data.get('email')
            
            if commit:
                cliente.save()

            # Crear la membresía asociada a este cliente (actualizado o nuevo)
            hoy = timezone.now().date()
            fecha_fin = hoy + timedelta(days=30)
            clases = getattr(servicio, 'cantidad_clases', 0)

            membresia = Membresia(
                cliente=cliente,
                servicio=servicio,
                fecha_fin=fecha_fin,
                clases_restantes=clases,
                activa=True,
                observaciones=observaciones
            )
            
            if commit:
                membresia.save()
                
            return membresia

class MembresiaEdicionForm(forms.ModelForm):
    # Campos de Cliente (se precargan con instance)
    nombre = forms.CharField(
        required=True, label="Nombre *",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'})
    )
    apellido = forms.CharField(
        required=True, label="Apellido *",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'})
    )
    dni = forms.CharField(
        required=True, label="DNI *",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'})
    )
    telefono = forms.CharField(
        required=True, label="Teléfono *",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'})
    )
    emergencia = forms.CharField(
        required=False, label="Teléfono de emergencia",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'})
    )
    domicilio = forms.CharField(
        required=False, label="Domicilio",
        widget=forms.TextInput(attrs={'class': 'form-control bg-transparent text-white'})
    )
    email = forms.EmailField(
        required=False, label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control bg-transparent text-white'})
    )

    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True).exclude(nombre__icontains='Por clase'),
        required=True, label="Servicio *",
        widget=forms.Select(attrs={'class': 'form-select bg-transparent text-white'})
    )
    observaciones = forms.CharField(
        required=False, label="Observaciones",
        widget=forms.Textarea(attrs={'class': 'form-control bg-transparent text-white'})
    )

    class Meta:
        model = Membresia
        fields = ['servicio', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            c = self.instance.cliente
            self.fields['nombre'].initial = c.nombre
            self.fields['apellido'].initial = c.apellido
            self.fields['dni'].initial = c.dni
            self.fields['telefono'].initial = c.telefono
            self.fields['emergencia'].initial = c.emergencia
            self.fields['domicilio'].initial = c.domicilio
            self.fields['email'].initial = c.email
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', nombre):
            raise ValidationError("El nombre solo puede contener letras y espacios.")
        return nombre.title()

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido', '').strip()
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', apellido):
            raise ValidationError("El apellido solo puede contener letras y espacios.")
        return apellido.title()

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '').strip()
        if not dni.isdigit():
            raise ValidationError("El DNI debe contener solo números.")
        if len(dni) < 7 or len(dni) > 8:
            raise ValidationError("El DNI debe tener entre 7 y 8 dígitos.")
        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
        if not re.match(r'^\+?[0-9]{8,15}$', telefono_limpio):
            raise ValidationError("Ingrese un número de teléfono válido (mínimo 8 dígitos).")
        return telefono

    def clean_emergencia(self):
        emergencia = self.cleaned_data.get('emergencia', '').strip()
        if emergencia:
            emergencia_limpio = re.sub(r'[\s\-\(\)]', '', emergencia)
            if not re.match(r'^\+?[0-9]{8,15}$', emergencia_limpio):
                raise ValidationError("Ingrese un número de emergencia válido (mínimo 8 dígitos).")
        return emergencia

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Ingrese un email válido.")
        return email
    
    def save(self, commit=True):
        servicio = self.cleaned_data['servicio']
        observaciones = self.cleaned_data.get('observaciones', '')

        # Actualizar cliente
        cliente = self.instance.cliente
        cliente.nombre = self.cleaned_data['nombre']
        cliente.apellido = self.cleaned_data['apellido']
        cliente.dni = self.cleaned_data['dni']
        cliente.telefono = self.cleaned_data['telefono']
        cliente.emergencia = self.cleaned_data.get('emergencia')
        cliente.domicilio = self.cleaned_data.get('domicilio')
        cliente.email = self.cleaned_data.get('email')
        if commit:
            cliente.save()

        # Actualizar membresía
        self.instance.servicio = servicio
        self.instance.observaciones = observaciones
        if commit:
            self.instance.save()
        return self.instance
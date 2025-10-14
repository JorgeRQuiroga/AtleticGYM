# servicios/forms.py
from django import forms
from .models import Servicio

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'cantidad_clases', 'precio']
        labels = {'nombre':   'Nombre del Servicio', 'cantidad': 'Cantidad de Clases', 'precio':   'Precio'}
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Yoga para principiantes'}),
            'cantidad': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej: 10','inputmode': 'numeric'}),
            'precio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1500.00', 'inputmode': 'decimal'}),
        }
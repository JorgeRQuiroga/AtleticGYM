# servicios/forms.py
from django import forms
from .models import Servicio

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'cantidad_clases', 'precio']
        labels = {'nombre':   'Nombre del Servicio', 'cantidad_clases': 'Cantidad de Clases', 'precio':   'Precio'}
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Yoga para principiantes'}),
            'cantidad_clases': forms.NumberInput(attrs={'class': 'form-control','placeholder': 'Ej: 10'}),
            'precio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1500.00', 'inputmode': 'decimal'}),
        }
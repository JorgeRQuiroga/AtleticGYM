# servicios/forms.py
from django import forms
from .models import Servicio

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'dias_semana', 'precio']
        labels = {'nombre':   'Nombre del Servicio','dias_semana': 'Días por Semana', 'precio':   'Precio' }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Yoga para principiantes'}),
            'dias_semana': forms.NumberInput(attrs={'class': 'form-control','placeholder': 'Ej: 3'}),
            'precio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1500.00', 'inputmode': 'decimal'}),
        }
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio

    def clean_cantidad_clases(self):
        cantidad = self.cleaned_data.get('cantidad_clases')
        if cantidad is not None and cantidad <= 0:
            raise forms.ValidationError("La cantidad de clases debe ser mayor a 0.")
        return cantidad
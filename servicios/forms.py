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
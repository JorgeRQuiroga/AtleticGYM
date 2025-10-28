from django import forms
from .models import Cobro, MetodoDePago
from servicios.models import Servicio

class CobroForm(forms.ModelForm):
    dni = forms.CharField(
        label="DNI del Cliente",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese DNI...'})
    )
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    metodo_pago = forms.ModelChoiceField(
        queryset=MetodoDePago.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Método de Pago"
    )

    class Meta:
        model = Cobro
        fields = ['descripcion']  # servicio y cliente se asignan en la vista
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
        }

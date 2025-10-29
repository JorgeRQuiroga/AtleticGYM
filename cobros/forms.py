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


class CobroClaseForm(forms.Form):
    dni = forms.CharField(
        label="DNI del Alumno",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese DNI...'})
    )
    metodo_pago = forms.ModelChoiceField(
        queryset=MetodoDePago.objects.all(),
        label="Método de Pago",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        servicio = Servicio.objects.get(nombre="Por clase")
        self.fields['servicio'] = forms.ModelChoiceField(
            queryset=Servicio.objects.filter(id=servicio.id),
            initial=servicio,
            widget=forms.Select(attrs={'class': 'form-select', 'readonly': 'readonly'})
        )
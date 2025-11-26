from django import forms
from .models import Cobro, MetodoDePago, Extraccion
from servicios.models import Servicio

class CobroForm(forms.ModelForm):
    dni = forms.CharField(
        label="DNI del Cliente",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese DNI...'})
    )
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-select bg-transparent text-white'}),
        required=False
    )
    metodo_pago = forms.ModelChoiceField(
        queryset=MetodoDePago.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select bg-transparent text-white'}),
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
        
class ExtraccionForm(forms.ModelForm):
    class Meta:
        model = Extraccion
        fields = ['monto', 'motivo']
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese monto a retirar'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'required': True,
                'placeholder': 'Motivo de la extracción'
            }),
        }
        

from django import forms
from .models import Cobro
from servicios.models import Servicio
from membresias.models import Membresia

class CobroForm(forms.ModelForm):
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.filter(activo=True),
        widget=forms.Select(attrs={'class':'form-select'})
    )
    dni = forms.CharField(
        label="DNI del Cliente",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Cobro
        fields = ['servicio', 'descripcion']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class':'form-control'}),
        }
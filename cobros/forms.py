from django import forms
from .models import Cobro
from servicios.models import Servicio

class CobroForm(forms.ModelForm):
    servicio = forms.ModelChoiceField(queryset=Servicio.objects.filter(activo=True), widget=forms.Select(attrs={'class':'form-select'}))

    class Meta:
        model = Cobro
        fields = ['servicio', 'descripcion']  # importe se completará automáticamente
        widgets = {
            'descripcion': forms.TextInput(attrs={'class':'form-control'}),
        }

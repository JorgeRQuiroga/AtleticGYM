from django import forms
from .models import Caja
from .models import Caja, ConfiguracionCaja

class AperturaCajaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = []

    def save(self, commit=True):
        instance = super().save(commit=False)
        config = ConfiguracionCaja.objects.first()
        if config:
            instance.monto_apertura = config.monto_inicial
        if commit:
            instance.save()
        return instance



class CierreCajaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = []

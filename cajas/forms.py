from django import forms
from .models import Caja

class AperturaCajaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = ['monto_apertura']

class CierreCajaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = []

from django import forms
from .models import Empleado
from django.contrib.auth.models import Group

class EmpleadoForm(forms.ModelForm):
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Rol (Grupo)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Empleado
        fields = ['user', 'nombre', 'apellido', 'dni', 'domicilio', 'telefono']
        labels = {
            'user': 'Usuario del sistema',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'dni': 'DNI',
            'domicilio': 'Domicilio',
            'telefono': 'Teléfono',
        }
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
from django import forms
from membresias.models import Membresia
from empleados.models import Empleado

class RegistroAsistenciaForm(forms.Form):
    tipo = forms.ChoiceField(
        choices=[('alumno', 'Alumno'), ('empleado', 'Empleado')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    membresia = forms.ModelChoiceField(
        queryset=Membresia.objects.filter(activa=True),
        required=False,
        label="Alumno (membresía activa)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    empleado = forms.ModelChoiceField(
        queryset=Empleado.objects.all(),
        required=False,
        label="Empleado (legajo)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

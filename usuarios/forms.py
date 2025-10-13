from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.models import User as Usuario
from usuarios.models import Empleado
from django.contrib.auth import get_user_model

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ********'
        }),
        required=True
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: ********'
        }),
        required=True
    )
    groups = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Grupo",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_groups'
        }),
        empty_label="Seleccionar grupo"
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name',
            'email',
            'password', 'password_confirm', 'groups'
        ]
        labels = {
            'username': 'Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: juanp'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pérez'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej: juan@example.com'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'type': 'text', 'placeholder': 'Ej: 30111222', 'inputmode': 'numeric', 'pattern': '[0-9]*'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3874123456'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Lista de campos obligatorios
        campos_obligatorios = ['username', 'first_name', 'last_name', 'email', 'dni', 'password', 'password_confirm', 'groups']
        for campo in campos_obligatorios:
            self.fields[campo].required = True

        # Campo opcional
        self.fields['telefono'].required = False

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])

        grupo = self.cleaned_data['groups']
        if grupo.name == 'Administrador':
            usuario.is_active = True
            usuario.is_staff = True
            usuario.is_superuser = True
        else:
            usuario.is_active = True
            usuario.is_staff = False
            usuario.is_superuser = False

        if commit:
            usuario.save()
            usuario.groups.set([grupo])
        return usuario

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['dni', 'telefono']

class AsisForm(forms.Form):
    dni = forms.IntegerField(
        label="Ingrese su DNI",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 30111222',
            'inputmode': 'numeric',
            'pattern': '[0-9]*'
        })
    )
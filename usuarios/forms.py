from django import forms
from django.contrib.auth.models import Group
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        required=True
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput,
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
            'email', 'dni', 'telefono',
            'password', 'password_confirm', 'groups'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Campos obligatorios (excepto teléfono)
        self.fields['username'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['dni'].required = True
        self.fields['password'].required = True
        self.fields['password_confirm'].required = True
        self.fields['groups'].required = True
        self.fields['telefono'].required = False

        # Estilos visuales
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input-estilo'})

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
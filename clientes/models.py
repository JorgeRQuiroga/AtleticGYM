from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
import re


def validar_dni(value):
    """Validador personalizado para DNI"""
    if not value:
        raise ValidationError("El DNI es obligatorio.")
    
    dni_str = str(value).strip()
    
    if not dni_str.isdigit():
        raise ValidationError("El DNI solo puede contener números.")
    
    if len(dni_str) < 7 or len(dni_str) > 8:
        raise ValidationError("El DNI debe tener entre 7 y 8 dígitos.")


def validar_telefono(value):
    """Validador personalizado para teléfonos"""
    if not value:
        return
    
    telefono_str = str(value).strip()
    telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono_str)
    
    if not re.match(r'^\+?[0-9]{8,15}$', telefono_limpio):
        raise ValidationError("Ingrese un número de teléfono válido (mínimo 8 dígitos).")


def validar_nombre(value):
    """Validador para nombres y apellidos"""
    if not value:
        raise ValidationError("Este campo es obligatorio.")
    
    nombre_str = str(value).strip()
    
    if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', nombre_str):
        raise ValidationError("Solo puede contener letras.")
    
    if len(nombre_str) < 2:
        raise ValidationError("Debe tener al menos 2 caracteres.")


class Cliente(models.Model):
    nombre = models.CharField(
        max_length=100,
        validators=[validar_nombre],
        help_text="Nombre del cliente"
    )
    apellido = models.CharField(
        max_length=100,
        validators=[validar_nombre],
        help_text="Apellido del cliente"
    )
    dni = models.CharField(
        max_length=8,
        validators=[validar_dni],
        help_text="Documento Nacional de Identidad (7-8 dígitos)"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        validators=[validar_telefono],
        help_text="Teléfono principal de contacto",
        default="0000000000"
    )
    emergencia = models.CharField(
        max_length=20,
        blank=True,
        validators=[validar_telefono],
        help_text="Teléfono de emergencia",        
        default="No especificado"
    )
    domicilio = models.CharField(
        max_length=200,
        blank=True,
        help_text="Dirección del cliente",
        default="No especificado"
    )
    email = models.EmailField(
        blank=True,
        validators=[EmailValidator(message="Ingrese un email válido")],
        help_text="Correo electrónico",
        default="No especificado"

    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el cliente está activo"
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['apellido', 'nombre']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI: {self.dni})"

    def clean(self):
        """Validaciones adicionales a nivel de modelo"""
        super().clean()
        
        # Normalizar datos
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        if self.apellido:
            self.apellido = self.apellido.strip().title()
        if self.dni:
            self.dni = self.dni.strip()
        if self.email:
            self.email = self.email.strip().lower()
        
        # Validar DNI único (excluyendo el objeto actual en ediciones)
        if self.dni:
            duplicados = Cliente.objects.filter(dni=self.dni).exclude(pk=self.pk)
            if duplicados.exists():
                raise ValidationError({
                    'dni': f'Ya existe un cliente con el DNI {self.dni}.'
                })

    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        super().save(*args, **kwargs)

    def get_nombre_completo(self):
        """Retorna el nombre completo del cliente"""
        return f"{self.nombre} {self.apellido}"

    def tiene_membresia_activa(self):
        """Verifica si el cliente tiene una membresía activa"""
        return hasattr(self, 'membresia') and self.membresia.activa

    def get_telefono_formateado(self):
        """Retorna el teléfono en formato legible"""
        # Ejemplo: 3814123456 -> (381) 412-3456
        if len(self.telefono) == 10:
            return f"({self.telefono[:3]}) {self.telefono[3:6]}-{self.telefono[6:]}"
        return self.telefono
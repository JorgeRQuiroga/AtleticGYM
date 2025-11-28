# yourapp/management/commands/generate_empleados.py
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from faker import Faker
from datetime import date
import random

from empleados.models import Empleado

User = get_user_model()

class Command(BaseCommand):
    help = 'Genera empleados ficticios y les asigna un usuario (username=password=DNI).'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=30, help='Cantidad mínima de empleados a crear')

    def handle(self, *args, **options):
        faker = Faker('es_AR')
        target = options['count']

        # Verificar campos requeridos en Empleado
        model_fields = [f.name for f in Empleado._meta.get_fields()]
        required = ['dni', 'nombre', 'apellido', 'telefono', 'domicilio']
        missing = [f for f in required if f not in model_fields]
        if missing:
            self.stdout.write(self.style.ERROR(
                f'El modelo Empleado no tiene los campos requeridos: {", ".join(missing)}.'
            ))
            return

        # Detectar campo de relación a User en Empleado (si existe)
        user_field = None
        for candidate in ('user', 'usuario', 'auth_user', 'usuario_id'):
            if candidate in model_fields:
                user_field = candidate
                break

        # Detectar campo de soft-delete (activo/eliminado)
        activo_field = None
        if 'activo' in model_fields:
            activo_field = 'activo'
        elif 'is_active' in model_fields:
            activo_field = 'is_active'
        elif 'eliminado' in model_fields:
            activo_field = 'eliminado'  # True = eliminado

        created = 0
        attempts = 0
        max_attempts = target * 6

        self.stdout.write(self.style.NOTICE(f'Generando hasta {target} empleados ficticios...'))

        with transaction.atomic():
            while created < target and attempts < max_attempts:
                attempts += 1
                dni = faker.unique.numerify(text='########')  # 8 dígitos
                nombre = faker.first_name()
                apellido = faker.last_name()
                telefono = faker.phone_number()
                domicilio = faker.address().replace('\n', ', ')

                try:
                    # Buscar empleado por DNI
                    try:
                        existing = Empleado.objects.get(dni=dni)
                    except Empleado.DoesNotExist:
                        existing = None

                    # Crear o actualizar usuario Django (username = dni, password = dni)
                    user = None
                    try:
                        user = User.objects.filter(username=dni).first()
                        if user:
                            user.set_password(dni)
                            user.save()
                        else:
                            # crear usuario; si el modelo User requiere email u otros campos, adaptá aquí
                            user = User.objects.create_user(username=dni, password=dni)
                    except Exception as e:
                        # No detener todo por un problema con el usuario; registrar y seguir
                        self.stdout.write(self.style.WARNING(f'No se pudo crear/actualizar User para DNI {dni}: {e}'))

                    if existing:
                        # Si existe, manejar reactivación si corresponde
                        if activo_field:
                            val = getattr(existing, activo_field)
                            if activo_field == 'eliminado':
                                is_active = not bool(val)
                            else:
                                is_active = bool(val)

                            if not is_active:
                                # Reactivar y actualizar datos
                                setattr(existing, 'nombre', nombre)
                                setattr(existing, 'apellido', apellido)
                                setattr(existing, 'telefono', telefono)
                                setattr(existing, 'domicilio', domicilio)
                                if user_field and user:
                                    setattr(existing, user_field, user)
                                # marcar activo según campo
                                if activo_field == 'eliminado':
                                    setattr(existing, activo_field, False)
                                else:
                                    setattr(existing, activo_field, True)
                                existing.save()
                                created += 1
                                continue
                            else:
                                # Ya existe activo: saltar este DNI
                                continue
                        else:
                            # No hay campo activo: si existe, saltar para evitar duplicados
                            continue
                    else:
                        # Crear nuevo empleado y asignar user si el campo existe
                        empleado_kwargs = {
                            'dni': dni,
                            'nombre': nombre,
                            'apellido': apellido,
                            'telefono': telefono,
                            'domicilio': domicilio
                        }
                        if user_field and user:
                            empleado_kwargs[user_field] = user

                        Empleado.objects.create(**empleado_kwargs)
                        created += 1

                except IntegrityError as e:
                    self.stdout.write(self.style.WARNING(f'IntegrityError: {e} (intento {attempts}/{max_attempts})'))
                    continue
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error inesperado: {e} (intento {attempts}/{max_attempts})'))
                    continue

        if created >= target:
            self.stdout.write(self.style.SUCCESS(f'Se generaron {created} empleados ficticios con usuario.'))
        else:
            self.stdout.write(self.style.WARNING(f'Se generaron {created} empleados (objetivo {target}). Intentos agotados.'))

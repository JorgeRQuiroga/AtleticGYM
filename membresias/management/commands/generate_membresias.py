# yourapp/management/commands/generate_membresias.py
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError
from faker import Faker
import random
from datetime import date, timedelta

from membresias.models import Cliente, Servicio, Membresia

class Command(BaseCommand):
    help = 'Genera membresías ficticias (clientes + membresías). Ignora servicios "Por Clase".'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=30, help='Cantidad mínima de membresías a crear')

    def handle(self, *args, **options):
        faker = Faker('es_AR')
        target = options['count']

        # Obtener servicios excluyendo los que sean "Por Clase" (comprobación por nombre)
        servicios_all = list(Servicio.objects.all())
        servicios = [s for s in servicios_all if 'por clase' not in (getattr(s, 'nombre', '') or '').lower()]

        if not servicios:
            self.stdout.write(self.style.ERROR(
                'No hay servicios válidos para generar membresías (todos son "Por Clase" o no existen).'
            ))
            return

        created = 0
        attempts = 0
        max_attempts = target * 5  # evita loop infinito si hay muchos duplicados

        self.stdout.write(self.style.NOTICE(f'Generando al menos {target} membresías ficticias (se omiten servicios "Por Clase")...'))

        with transaction.atomic():
            while created < target and attempts < max_attempts:
                attempts += 1

                # Generar datos de cliente
                dni = faker.unique.numerify(text='########')  # 8 dígitos; ajustá si necesitás otro formato
                nombre = faker.first_name()
                apellido = faker.last_name()
                telefono = faker.phone_number()

                servicio = random.choice(servicios)

                # Determinar cantidad de clases_restantes a partir del servicio
                # Se buscan varios nombres posibles de campo en el modelo Servicio
                clases_val = None
                for attr in ('clases_restantes', 'clases', 'cantidad_clases', 'numero_clases'):
                    if hasattr(servicio, attr):
                        clases_val = getattr(servicio, attr)
                        break

                # Fechas: inicio = hoy, vencimiento = hoy + 30 días
                hoy = date.today()
                fecha_inicio = hoy
                fecha_fin = hoy + timedelta(days=30)

                try:
                    cliente, cliente_created = Cliente.objects.get_or_create(
                        dni=dni,
                        defaults={'nombre': nombre, 'apellido': apellido, 'telefono': telefono}
                    )

                    # Preparar kwargs dinámicos para crear la Membresia
                    memb_kwargs = {
                        'cliente': cliente,
                        'servicio': servicio,
                        # si tus campos de fecha se llaman distinto, ajustá aquí
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'activa': True
                    }

                    # Si el modelo Membresia tiene un campo 'clases_restantes' (o similar),
                    # asignamos el valor obtenido del servicio
                    # Buscamos el nombre exacto del campo en Membresia
                    memb_field_name = None
                    for candidate in ('clases_restantes', 'clases_restantes_membresia', 'clases', 'clases_rest'):
                        try:
                            Membresia._meta.get_field(candidate)
                            memb_field_name = candidate
                            break
                        except Exception:
                            continue

                    if memb_field_name and clases_val is not None:
                        memb_kwargs[memb_field_name] = clases_val

                    # Crear la membresía
                    Membresia.objects.create(**memb_kwargs)
                    created += 1

                except IntegrityError as e:
                    self.stdout.write(self.style.WARNING(f'IntegrityError al crear registro: {e}. Intento {attempts}/{max_attempts}'))
                    continue
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Error inesperado: {e}'))
                    continue

        if created >= target:
            self.stdout.write(self.style.SUCCESS(f'Se generaron {created} membresías ficticias.'))
        else:
            self.stdout.write(self.style.WARNING(f'Se generaron {created} membresías (objetivo {target}). Intentos agotados.'))

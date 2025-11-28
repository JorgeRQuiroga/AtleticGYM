# yourapp/management/commands/generate_min_asistencias.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime, time, date
import random
from faker import Faker

from asistencias.models import Membresia, Asistencia

class Command(BaseCommand):
    help = 'Asegura que cada membresía activa tenga al menos N asistencias en los últimos D días.'

    def add_arguments(self, parser):
        parser.add_argument('--min-per-member', type=int, default=4,
                            help='Mínimo de asistencias por membresía en el período (por defecto 4).')
        parser.add_argument('--days', type=int, default=15,
                            help='Cantidad de días hacia atrás para distribuir las asistencias (por defecto 15).')
        parser.add_argument('--seed', type=int, default=None,
                            help='Semilla opcional para reproducibilidad.')

    def handle(self, *args, **options):
        faker = Faker('es_AR')
        seed = options.get('seed')
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)

        min_per_member = options['min_per_member']
        days = options['days']

        # Obtener 'hoy' de forma robusta evitando localdate() sobre un datetime naive
        now = timezone.now()
        if timezone.is_naive(now):
            hoy = date.today()
        else:
            hoy = timezone.localdate(now)
        inicio = hoy - timedelta(days=days)

        # Helper: convertir datetime naive a aware solo si USE_TZ está activado
        def make_aware_if_needed(dt: datetime) -> datetime:
            if not isinstance(dt, datetime):
                return dt
            if settings.USE_TZ:
                if timezone.is_naive(dt):
                    return timezone.make_aware(dt, timezone.get_current_timezone())
                return dt
            return dt

        # Seleccionar membresías activas cuyo rango intersecta el período
        membresias_qs = Membresia.objects.filter(
            activa=True,
            fecha_fin__gte=inicio,
            fecha_inicio__lte=hoy
        ).select_related('cliente')

        if not membresias_qs.exists():
            self.stdout.write(self.style.WARNING('No se encontraron membresías activas en el período indicado.'))
            return

        to_create = []
        membresias_to_update = []
        total_new = 0

        for m in membresias_qs:
            # contar asistencias ya registradas para esta membresía en el rango [inicio, hoy]
            existing_count = Asistencia.objects.filter(
                membresia=m,
                fecha_hora__date__gte=inicio,
                fecha_hora__date__lte=hoy
            ).count()

            needed = max(0, min_per_member - existing_count)
            if needed <= 0:
                continue

            # construir lista de días disponibles en el rango
            all_days = [(inicio + timedelta(days=i)) for i in range((hoy - inicio).days + 1)]
            # obtener días ya usados por esta membresía para evitar duplicados por día
            used_days_qs = Asistencia.objects.filter(
                membresia=m,
                fecha_hora__date__gte=inicio,
                fecha_hora__date__lte=hoy
            ).values_list('fecha_hora__date', flat=True)
            used_days = set(d for d in used_days_qs)

            available_days = [d for d in all_days if d not in used_days]
            # si no hay suficientes días disponibles, permitimos reutilizar días (se generarán con distinta hora)
            if len(available_days) >= needed:
                chosen_days = sorted(random.sample(available_days, k=needed))
            else:
                # tomar todos los disponibles y completar con días aleatorios del rango (posibles repeticiones de día)
                chosen_days = list(available_days)
                extra_needed = needed - len(chosen_days)
                if all_days:
                    chosen_days += [random.choice(all_days) for _ in range(extra_needed)]
                    chosen_days = sorted(chosen_days)
                else:
                    # no hay días (caso extremo), saltar
                    continue

            # Simular consumo de clases en orden cronológico
            current_clases = m.clases_restantes if m.clases_restantes is not None else 0

            for day in chosen_days:
                # hora aleatoria entre 06:00 y 22:00
                hour = random.randint(6, 21)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                dt = datetime.combine(day, time(hour, minute, second))
                dt = make_aware_if_needed(dt)

                clases_al_momento = current_clases if current_clases > 0 else 0

                a = Asistencia(
                    membresia=m,
                    fecha_hora=dt,
                    clases_al_momento=clases_al_momento
                )
                to_create.append(a)
                total_new += 1

                # consumir una clase si había disponibles
                if current_clases > 0:
                    current_clases -= 1

            # actualizar la membresía en memoria
            m.clases_restantes = current_clases
            if m.clases_restantes <= 0:
                m.activa = False
            membresias_to_update.append(m)

        # Guardar en DB
        with transaction.atomic():
            if to_create:
                Asistencia.objects.bulk_create(to_create)
            for m in membresias_to_update:
                m.save()

        self.stdout.write(self.style.SUCCESS(
            f'Se generaron {total_new} asistencias para {len(membresias_to_update)} membresías. '
            f'Cada membresía ahora tiene al menos {min_per_member} asistencias en los últimos {days} días (si fue posible).'
        ))

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum

from torneos.models import ParticipacionJugador, Goleador, GoleadorJornada


class Command(BaseCommand):
    help = 'Consolida goleadores a partir de participaciones existentes en partidos marcados como jugados.'

    def handle(self, *args, **options):
        qs = ParticipacionJugador.objects.select_related('jugador', 'partido', 'partido__grupo', 'partido__grupo__categoria').filter(partido__jugado=True)
        total_participaciones = qs.count()
        created_goleadores = 0
        created_jornadas = 0
        skipped_jornadas = 0

        self.stdout.write(f'Procesando {total_participaciones} participaciones en partidos jugados...')

        # Procesar por participacion
        with transaction.atomic():
            for participacion in qs.iterator():
                partido = participacion.partido
                jugador = participacion.jugador

                # Determinar categoría si existe
                categoria = None
                grupo = getattr(partido, 'grupo', None)
                if grupo and getattr(grupo, 'categoria', None):
                    categoria = grupo.categoria

                goleador, gcreated = Goleador.objects.get_or_create(jugador=jugador, categoria=categoria, defaults={'goles': 0})
                if gcreated:
                    created_goleadores += 1

                # Crear jornada si no existe
                exists = GoleadorJornada.objects.filter(goleador=goleador, partido=partido).exists()
                if not exists:
                    GoleadorJornada.objects.create(goleador=goleador, partido=partido, goles=0)
                    created_jornadas += 1
                else:
                    skipped_jornadas += 1

        # Recalcular totales por goleador
        goleadores = Goleador.objects.all()
        for g in goleadores.iterator():
            total = GoleadorJornada.objects.filter(goleador=g).aggregate(total=Sum('goles'))['total'] or 0
            if g.goles != total:
                g.goles = total
                g.save()

        self.stdout.write(self.style.SUCCESS(f'Creados {created_goleadores} goleador(es) nuevos.'))
        self.stdout.write(self.style.SUCCESS(f'Creadas {created_jornadas} jornada(s) nuevas.'))
        self.stdout.write(self.style.WARNING(f'Se saltaron {skipped_jornadas} jornadas porque ya existían.'))
        self.stdout.write(self.style.SUCCESS('Consolidación completada.'))

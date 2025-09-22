from django.core.management.base import BaseCommand
from ...models import Torneo, Equipo, Jugador
import os

class Command(BaseCommand):
    help = 'Elimina todas las imágenes asociadas a un torneo específico'

    def add_arguments(self, parser):
        parser.add_argument('--tournament', type=int, required=True, help='ID del torneo')

    def handle(self, *args, **options):
        tournament_id = options['tournament']
        try:
            torneo = Torneo.objects.get(id=tournament_id)
        except Torneo.DoesNotExist:
            self.stderr.write(f'Torneo con ID {tournament_id} no encontrado.')
            return

        self.stdout.write(f'Eliminando imágenes para el torneo: {torneo.nombre}')

        # Eliminar logo del torneo
        if torneo.logo:
            if os.path.exists(torneo.logo.path):
                os.remove(torneo.logo.path)
                self.stdout.write(f'Logo del torneo eliminado: {torneo.logo.path}')
            torneo.logo = None
            torneo.color1 = None
            torneo.color2 = None
            torneo.color3 = None
            torneo.save(update_fields=['logo', 'color1', 'color2', 'color3'])

        # Eliminar logos de equipos en las categorías del torneo
        equipos = Equipo.objects.filter(categoria__torneo=torneo)
        for equipo in equipos:
            if equipo.logo:
                if os.path.exists(equipo.logo.path):
                    os.remove(equipo.logo.path)
                    self.stdout.write(f'Logo del equipo {equipo.nombre} eliminado: {equipo.logo.path}')
                equipo.logo = None
                equipo.save(update_fields=['logo'])

        # Eliminar fotos de jugadores en equipos del torneo
        jugadores = Jugador.objects.filter(equipo__categoria__torneo=torneo)
        for jugador in jugadores:
            if jugador.foto:
                if os.path.exists(jugador.foto.path):
                    os.remove(jugador.foto.path)
                    self.stdout.write(f'Foto del jugador {jugador.nombre} {jugador.apellido} eliminada: {jugador.foto.path}')
                jugador.foto = None
                jugador.save(update_fields=['foto'])

        self.stdout.write(f'Imágenes eliminadas para el torneo {torneo.nombre}.')
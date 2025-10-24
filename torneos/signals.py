from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum

from .models import ParticipacionJugador, Goleador, GoleadorJornada


@receiver(post_save, sender=ParticipacionJugador)
def ensure_goleador_on_participacion(sender, instance, created, **kwargs):
    """Al crear una ParticipacionJugador, si el partido está marcado como jugado,
    asegurar que exista un Goleador padre y una GoleadorJornada asociada con 0 goles.
    Esto cubre todas las vías de creación (admin, imports, scripts).
    """
    try:
        partido = instance.partido
        if not partido:
            return
        if not getattr(partido, 'jugado', False):
            return

        jugador = instance.jugador
        # Determinar categoría si el partido pertenece a un grupo
        categoria = None
        if getattr(partido, 'grupo', None) and getattr(partido.grupo, 'categoria', None):
            categoria = partido.grupo.categoria

        goleador, _ = Goleador.objects.get_or_create(jugador=jugador, categoria=categoria, defaults={'goles': 0})
        # Si no existe jornada para ese partido, crear con 0 goles
        exists = GoleadorJornada.objects.filter(goleador=goleador, partido=partido).exists()
        if not exists:
            GoleadorJornada.objects.create(goleador=goleador, partido=partido, goles=0)
            total = GoleadorJornada.objects.filter(goleador=goleador).aggregate(total=Sum('goles'))['total'] or 0
            goleador.goles = total
            goleador.save()
    except Exception:
        # No queremos fallar la transacción principal si algo sale mal aquí
        pass

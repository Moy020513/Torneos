from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Partido, ParticipacionJugador, Jugador, Sancion


def is_arbitro(user):
    return hasattr(user, 'arbitro') and getattr(user.arbitro, 'activo', False)


def _sancion_tiene_contenido(sancion):
    """Determina si una sancion tiene datos reales para persistirse/mostrarse."""
    tipo_tarjeta = (sancion.tipo_tarjeta or 'ninguna')
    cantidad_amarillas = sancion.cantidad_amarillas or 0
    tipo_roja = (sancion.tipo_roja or '').strip()
    observaciones = (sancion.observaciones or '').strip()

    if tipo_tarjeta != 'ninguna':
        return True
    if cantidad_amarillas > 0:
        return True
    if tipo_roja:
        return True
    if observaciones:
        return True
    return False

@login_required
@user_passes_test(is_arbitro)
def arbitro_partido_sanciones(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id, arbitro=request.user.arbitro)
    participaciones = ParticipacionJugador.objects.filter(partido=partido).select_related('jugador', 'jugador__equipo')
    if not participaciones.exists():
        messages.warning(request, 'Primero tienes que registrar participaciones de los jugadores.')
        return redirect('arbitro_partido_participaciones', partido_id=partido.id)

    equipos = {}
    for p in participaciones:
        eq = p.jugador.equipo
        if eq.id not in equipos:
            equipos[eq.id] = {'equipo': eq, 'jugadores': []}
        equipos[eq.id]['jugadores'].append(p.jugador)

    # Solo mostrar sanciones con contenido real.
    sanciones_dict = {
        s.jugador_id: s
        for s in Sancion.objects.filter(partido=partido)
        if _sancion_tiene_contenido(s)
    }

    context = {
        'partido': partido,
        'equipos': equipos,
        'sanciones_dict': sanciones_dict,
    }
    return render(request, 'torneos/arbitro/partido_sanciones_lista.html', context)

@login_required
@user_passes_test(is_arbitro)
def arbitro_sancion_editar(request, partido_id, jugador_id):
    from .forms import SancionForm
    partido = get_object_or_404(Partido, id=partido_id, arbitro=request.user.arbitro)
    jugador = get_object_or_404(Jugador, id=jugador_id)
    sancion_existente = Sancion.objects.filter(partido=partido, jugador=jugador).first()

    if request.method == 'POST':
        instancia = sancion_existente or Sancion(partido=partido, jugador=jugador)
        form = SancionForm(request.POST, instance=instancia)
        if form.is_valid():
            sancion = form.save(commit=False)
            sancion.partido = partido
            sancion.jugador = jugador

            if _sancion_tiene_contenido(sancion):
                sancion.save()
                messages.success(request, 'Sanción guardada correctamente.')
            else:
                if sancion.pk:
                    sancion.delete()
                messages.info(request, 'No se registró sanción para este jugador.')
            return redirect('arbitro_partido_sanciones', partido_id=partido.id)
    else:
        form = SancionForm(instance=sancion_existente)

    context = {
        'form': form,
        'partido': partido,
        'jugador': jugador,
    }
    return render(request, 'torneos/arbitro/partido_sancion_editar.html', context)

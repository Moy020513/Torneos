from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Partido, ParticipacionJugador, Jugador, Sancion

def is_arbitro(user):
    return hasattr(user, 'arbitro') and getattr(user.arbitro, 'activo', False)

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

    # Consultar sanciones por jugador en este partido
    sanciones_dict = {s.jugador_id: s for s in Sancion.objects.filter(partido=partido)}

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
    sancion, _ = Sancion.objects.get_or_create(partido=partido, jugador=jugador)

    if request.method == 'POST':
        form = SancionForm(request.POST, instance=sancion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sanción guardada correctamente.')
            return redirect('arbitro_partido_sanciones', partido_id=partido.id)
    else:
        form = SancionForm(instance=sancion)

    context = {
        'form': form,
        'partido': partido,
        'jugador': jugador,
    }
    return render(request, 'torneos/arbitro/partido_sancion_editar.html', context)

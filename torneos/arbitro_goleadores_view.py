from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Partido, ParticipacionJugador, Jugador, Goleador
from .forms import GoleadorForm

def is_arbitro(user):
    return hasattr(user, 'arbitro') and getattr(user.arbitro, 'activo', False)

@login_required
@user_passes_test(is_arbitro)
def arbitro_partido_goleadores(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id, arbitro=request.user.arbitro)
    participaciones = ParticipacionJugador.objects.filter(partido=partido).select_related('jugador', 'jugador__equipo')
    if not participaciones.exists():
        messages.warning(request, 'Primero tienes que registrar participaciones de los jugadores.')
        return redirect('arbitro_partido_participaciones', partido_id=partido.id)

    # Agrupar por equipo
    equipos = {}
    for p in participaciones:
        eq = p.jugador.equipo
        if eq.id not in equipos:
            equipos[eq.id] = {'equipo': eq, 'jugadores': []}
        equipos[eq.id]['jugadores'].append(p.jugador)

    # Obtener goles por jugador en este partido
    goles_dict = {g.jugador_id: g for g in Goleador.objects.filter(partido=partido)}

    context = {
        'partido': partido,
        'equipos': equipos,
        'goles_dict': goles_dict,
    }
    return render(request, 'torneos/arbitro/partido_goleadores_lista.html', context)


# Nueva vista para editar goles de un jugador en un template aparte
@login_required
@user_passes_test(is_arbitro)
def arbitro_goleador_editar(request, partido_id, jugador_id):
    partido = get_object_or_404(Partido, id=partido_id, arbitro=request.user.arbitro)
    jugador = get_object_or_404(Jugador, id=jugador_id)
    goleador, created = Goleador.objects.get_or_create(partido=partido, jugador=jugador, defaults={
        'categoria': partido.grupo.categoria if partido.grupo else partido.equipo_local.categoria,
        'goles': 0
    })
    if request.method == 'POST':
        form = GoleadorForm(request.POST, instance=goleador)
        form.fields['jugador'].widget = forms.HiddenInput()
        form.fields['partido'].widget = forms.HiddenInput()
        form.fields['partido_eliminatoria'].widget = forms.HiddenInput()
        form.fields['categoria'].widget = forms.HiddenInput()
        if form.is_valid():
            form.save()
            messages.success(request, 'Goles actualizados correctamente.')
            return redirect('arbitro_partido_goleadores', partido_id=partido.id)
    else:
        form = GoleadorForm(instance=goleador)
        form.fields['jugador'].widget = forms.HiddenInput()
        form.fields['partido'].widget = forms.HiddenInput()
        form.fields['partido_eliminatoria'].widget = forms.HiddenInput()
        form.fields['categoria'].widget = forms.HiddenInput()
    return render(request, 'torneos/arbitro/partido_goleador_form.html', {'form': form, 'partido': partido, 'jugador': jugador})

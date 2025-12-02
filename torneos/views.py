def jugadores_view(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = Equipo.objects.filter(categoria=categoria)
    context = {
        'categoria': categoria,
        'equipos': equipos
    }
    return render(request, 'torneos/jugadores.html', context)
# Vista independiente para resultados
def resultados_view(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = Equipo.objects.filter(categoria=categoria)
    partidos = Partido.objects.filter(
        Q(grupo__categoria=categoria) |
        Q(grupo=None, equipo_local__categoria=categoria) |
        Q(grupo=None, equipo_visitante__categoria=categoria)
    )
    # Incluir partidos con goles aunque jugado no esté marcado aún
    ultimos_resultados = partidos.filter(
        Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
    ).order_by('-fecha')[:50]
    jornadas = sorted(set(p.jornada for p in ultimos_resultados))
    context = {
        'categoria': categoria,
        'equipos': equipos,
        'ultimos_resultados': ultimos_resultados,
        'jornadas': jornadas
    }
    return render(request, 'torneos/resultados.html', context)
# Vista de estadísticas solo para administradores
from django.contrib.auth.decorators import user_passes_test

def estadisticas_view(request, categoria_id):
    # Determinar si el usuario actual es admin; si no lo es, se le mostrará
    # únicamente las gráficas (sin las tarjetas de totales/paneles).
    is_admin_view = request.user.is_authenticated and request.user.is_superuser
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = Equipo.objects.filter(categoria=categoria)
    partidos = Partido.objects.filter(
        Q(grupo__categoria=categoria) |
        Q(grupo=None, equipo_local__categoria=categoria) |
        Q(grupo=None, equipo_visitante__categoria=categoria)
    )
    # Excluir partidos de descanso (local == visitante) de las estadísticas
    partidos_sin_descanso = partidos.exclude(equipo_local=F('equipo_visitante'))

    # Partidos válidos como jugados: jugado=True o con goles cargados
    partidos_jugados_query = partidos_sin_descanso.filter(
        Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
    )
    # Próximos partidos: no jugados y sin goles (sin incluir descansos)
    proximos_partidos = partidos_sin_descanso.filter(jugado=False, goles_local=0, goles_visitante=0).order_by('fecha')[:10]
    ultimos_resultados = partidos_jugados_query.order_by('-fecha')[:10]
    # Partidos para graficar: priorizar partidos ya jugados y luego por fecha
    # para asegurarnos de que los encuentros finalizados (con goles)
    # estén presentes en la muestra usada por el gráfico.
    partidos_para_grafico = partidos_sin_descanso.order_by('-jugado', '-fecha')[:50]
    # Jornadas totales existentes en la categoría (usar para mostrar eje X completo)
    jornadas_categoria = sorted(set(p.jornada for p in partidos_sin_descanso if p.jornada is not None))
    total_partidos = partidos_sin_descanso.count()
    partidos_jugados = partidos_jugados_query.count()
    partidos_pendientes = partidos_sin_descanso.filter(jugado=False, goles_local=0, goles_visitante=0).count()
    total_goles_local = partidos_jugados_query.aggregate(Sum('goles_local'))['goles_local__sum'] or 0
    total_goles_visitante = partidos_jugados_query.aggregate(Sum('goles_visitante'))['goles_visitante__sum'] or 0
    total_goles = total_goles_local + total_goles_visitante
    context = {
        'categoria': categoria,
        'equipos': equipos,
        'proximos_partidos': proximos_partidos,
        'ultimos_resultados': ultimos_resultados,
    'partidos_para_grafico': partidos_para_grafico,
    'jornadas_categoria': jornadas_categoria,
        'total_partidos': total_partidos,
        'partidos_jugados': partidos_jugados,
        'partidos_pendientes': partidos_pendientes,
        'total_goles': total_goles,
        'is_admin_view': is_admin_view,
    }
    return render(request, 'torneos/estadisticas.html', context)
# AJAX para filtrar categorías por torneo en el admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
@staff_member_required
def get_categorias_by_torneo(request):
    torneo_id = request.GET.get('torneo_id')
    categorias = []
    if torneo_id:
        categorias_qs = Categoria.objects.filter(torneo_id=torneo_id).values('id', 'nombre')
        categorias = list(categorias_qs)
    return JsonResponse({'categorias': categorias})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import admin_torneo_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F
from .models import *
from .forms import *
import json
from datetime import datetime
from django.utils import timezone
from django.conf import settings


def is_admin(user):
    # Un administrador del sistema (superuser) o un usuario asignado como
    # AdministradorTorneo activo deben considerarse administradores.
    try:
        if user.is_superuser:
            return True
    except Exception:
        # user may be None or not fully populated
        return False

    if not getattr(user, 'is_authenticated', False):
        return False

    # AdministradorTorneo viene de models (imported with *)
    return AdministradorTorneo.objects.filter(usuario=user, activo=True).exists()

def is_capitan(user):
    return hasattr(user, 'capitan') and user.capitan.activo

# Panel principal del capitán
from django.urls import reverse
from django.http import HttpResponseForbidden

@login_required
@user_passes_test(is_capitan)
def capitan_panel(request):
    capitan = request.user.capitan
    equipo = capitan.equipo
    jugadores = Jugador.objects.filter(equipo=equipo)
    context = {
        'capitan': capitan,
        'equipo': equipo,
        'jugadores': jugadores,
    }
    return render(request, 'torneos/capitan/panel.html', context)

# CRUD de jugadores para capitán
@login_required
@user_passes_test(is_capitan)
def capitan_jugador_create(request):
    equipo = request.user.capitan.equipo
    from .forms import CapitanJugadorForm
    if request.method == 'POST':
        form = CapitanJugadorForm(request.POST, request.FILES)
        if form.is_valid():
            jugador = form.save(commit=False)
            jugador.equipo = equipo
            # Forzar mayúsculas en el nombre y apellido
            jugador.nombre = jugador.nombre.upper() if jugador.nombre else ''
            jugador.apellido = jugador.apellido.upper() if jugador.apellido else ''
            jugador.save()
            messages.success(request, 'Jugador creado exitosamente.')
            return redirect('capitan_panel')
    else:
        form = CapitanJugadorForm()
    return render(request, 'torneos/capitan/jugador_form.html', {'form': form})

@login_required
@user_passes_test(is_capitan)
def capitan_jugador_update(request, jugador_id):
    equipo = request.user.capitan.equipo
    jugador = get_object_or_404(Jugador, id=jugador_id, equipo=equipo)
    # Si el jugador ya está verificado por un administrador, impedir edición por capitán
    if getattr(jugador, 'verificado', False):
        messages.warning(request, 'Este jugador ha sido verificado por un administrador y no puede ser editado por el capitán. Solo puede ser eliminado.')
        return redirect('capitan_panel')
    from .forms import CapitanJugadorForm
    if request.method == 'POST':
        form = CapitanJugadorForm(request.POST, request.FILES, instance=jugador)
        if form.is_valid():
            jugador = form.save(commit=False)
            # Forzar mayúsculas en el nombre y apellido
            jugador.nombre = jugador.nombre.upper() if jugador.nombre else ''
            jugador.apellido = jugador.apellido.upper() if jugador.apellido else ''
            jugador.save()
            messages.success(request, 'Jugador actualizado.')
            return redirect('capitan_panel')
    else:
        form = CapitanJugadorForm(instance=jugador)
    return render(request, 'torneos/capitan/jugador_form.html', {'form': form, 'jugador': jugador})

@login_required
@user_passes_test(is_capitan)
def capitan_jugador_delete(request, jugador_id):
    equipo = request.user.capitan.equipo
    jugador = get_object_or_404(Jugador, id=jugador_id, equipo=equipo)
    if request.method == 'POST':
        jugador.delete()
        messages.success(request, 'Jugador eliminado.')
        return redirect('capitan_panel')
    return render(request, 'torneos/capitan/jugador_confirm_delete.html', {'jugador': jugador})

def index(request):
    torneos_activos = Torneo.objects.filter(activo=True)
    
    # Estadísticas para el dashboard
    total_torneos = Torneo.objects.count()
    total_equipos = Equipo.objects.count()
    total_jugadores = Jugador.objects.count()
    total_partidos = Partido.objects.count()
    
    context = {
        'torneos': torneos_activos,
        'total_torneos': total_torneos,
        'total_equipos': total_equipos,
        'total_jugadores': total_jugadores,
        'total_partidos': total_partidos,
    }
    return render(request, 'torneos/index.html', context)

def torneo_detalle(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    categorias = Categoria.objects.filter(torneo=torneo)
    # Calcular el total de equipos en todas las categorías del torneo
    from .models import Equipo
    total_equipos = Equipo.objects.filter(categoria__in=categorias).count()
    context = {
        'torneo': torneo,
        'categorias': categorias,
        'total_equipos': total_equipos
    }
    return render(request, 'torneos/torneo_detalle.html', context)


def categoria_detalle(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = Equipo.objects.filter(categoria=categoria)
    partidos = Partido.objects.filter(
        Q(grupo__categoria=categoria) |
        Q(grupo=None, equipo_local__categoria=categoria) |
        Q(grupo=None, equipo_visitante__categoria=categoria)
    )
    # Próximos enfrentamientos (no jugados y sin goles cargados)
    proximos_partidos = list(partidos.filter(jugado=False, goles_local=0, goles_visitante=0))
    # Ordenar: primero por fecha si existe, si no por jornada
    def _proximo_sort_key(p):
        dt = p.fecha
        if settings.USE_TZ:
            if dt is None:
                dt_use = timezone.make_aware(datetime(9999, 12, 31, 0, 0, 0))
            else:
                dt_use = dt if timezone.is_aware(dt) else timezone.make_aware(dt)
        else:
            if dt is None:
                dt_use = datetime(9999, 12, 31, 0, 0, 0)
            else:
                dt_use = dt if timezone.is_naive(dt) else timezone.make_naive(dt)
        return (dt_use, p.jornada or 9999)

    proximos_partidos.sort(key=_proximo_sort_key)
    # Incluir partidos de descanso entre los próximos sólo si en la misma
    # jornada existen otros partidos pendientes (no-descanso).
    # Construimos el set de jornadas que tienen al menos un partido
    # pendiente que NO sea de descanso.
    jornadas_con_partidos_pendientes = set()
    for p in partidos.filter(jugado=False, goles_local=0, goles_visitante=0):
        # si no es descanso, marcar la jornada como con pendientes
        if not (p.equipo_local and p.equipo_visitante and p.equipo_local == p.equipo_visitante):
            if p.jornada is not None:
                jornadas_con_partidos_pendientes.add(p.jornada)

    # Filtrar proximos_partidos: mantener partidos normales; mantener
    # partidos de descanso sólo si su jornada está en jornadas_con_partidos_pendientes
    proximos_partidos = [
        p for p in proximos_partidos
        if not (p.equipo_local and p.equipo_visitante and p.equipo_local == p.equipo_visitante)
        or (p.jornada in jornadas_con_partidos_pendientes)
    ]
    # Últimos resultados (partidos con goles cargados o marcados como jugados)
    partidos_jugados_query = partidos.filter(
        Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
    )
    ultimos_resultados = partidos_jugados_query.order_by('-fecha')[:10]
    # Estadísticas generales
    total_partidos = partidos.count()
    partidos_jugados = partidos_jugados_query.count()
    partidos_pendientes = partidos.filter(jugado=False, goles_local=0, goles_visitante=0).count()
    total_goles_local = partidos_jugados_query.aggregate(Sum('goles_local'))['goles_local__sum'] or 0
    total_goles_visitante = partidos_jugados_query.aggregate(Sum('goles_visitante'))['goles_visitante__sum'] or 0
    total_goles = total_goles_local + total_goles_visitante
    # Obtener estadísticas de equipos
    for equipo in equipos:
        # Usar la misma lógica: partidos con jugado=True o con goles > 0
        partidos_jugados_eq = Partido.objects.filter(
            Q(equipo_local=equipo) | Q(equipo_visitante=equipo)
        ).filter(
            Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
        ).count()
        
        partidos_ganados = Partido.objects.filter(
            Q(equipo_local=equipo, goles_local__gt=F('goles_visitante')) |
            Q(equipo_visitante=equipo, goles_visitante__gt=F('goles_local'))
        ).filter(
            Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
        ).count()
        
        partidos_empatados = Partido.objects.filter(
            Q(equipo_local=equipo, goles_local=F('goles_visitante')) |
            Q(equipo_visitante=equipo, goles_visitante=F('goles_local'))
        ).filter(
            Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
        ).count()
        
        partidos_perdidos = partidos_jugados_eq - partidos_ganados - partidos_empatados
        
        goles_favor = Partido.objects.filter(
            Q(equipo_local=equipo)
        ).filter(
            Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
        ).aggregate(total=Sum('goles_local'))['total'] or 0
        goles_favor += Partido.objects.filter(
            Q(equipo_visitante=equipo)
        ).filter(
            Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
        ).aggregate(total=Sum('goles_visitante'))['total'] or 0
        
        goles_contra = Partido.objects.filter(
            Q(equipo_local=equipo)
        ).filter(
            Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
        ).aggregate(total=Sum('goles_visitante'))['total'] or 0
        goles_contra += Partido.objects.filter(
            Q(equipo_visitante=equipo)
        ).filter(
            Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
        ).aggregate(total=Sum('goles_local'))['total'] or 0
        
        diferencia_goles = goles_favor - goles_contra
        puntos = (partidos_ganados * 3) + partidos_empatados
        equipo.partidos_jugados = partidos_jugados_eq
        equipo.partidos_ganados = partidos_ganados
        equipo.partidos_empatados = partidos_empatados
        equipo.partidos_perdidos = partidos_perdidos
        equipo.goles_favor = goles_favor
        equipo.goles_contra = goles_contra
        equipo.diferencia_goles = diferencia_goles
        equipo.puntos = puntos
    equipos = sorted(equipos, key=lambda x: (-x.puntos, -x.diferencia_goles, -x.goles_favor))
    # Obtener jornadas únicas para el filtro
    jornadas = sorted(set(p.jornada for p in proximos_partidos))
    context = {
        'categoria': categoria,
        'equipos': equipos,
        'proximos_partidos': proximos_partidos,
        'ultimos_resultados': ultimos_resultados,
        'total_partidos': total_partidos,
        'partidos_jugados': partidos_jugados,
        'partidos_pendientes': partidos_pendientes,
        'total_goles': total_goles,
        'jornadas': jornadas,
    }
    return render(request, 'torneos/categoria_detalle.html', context)
@login_required
@user_passes_test(is_admin)
def administracion_dashboard(request):
    # Si el usuario es AdministradorTorneo, limitar a su torneo
    assigned_torneo = None
    try:
        if not request.user.is_superuser:
            assigned_torneo = AdministradorTorneo.objects.filter(usuario=request.user, activo=True).values_list('torneo_id', flat=True).first()
    except Exception:
        assigned_torneo = None

    if assigned_torneo:
        torneos = Torneo.objects.filter(id=assigned_torneo)
        categorias = Categoria.objects.filter(torneo_id=assigned_torneo)
        equipos = Equipo.objects.filter(categoria__torneo_id=assigned_torneo)
        jugadores = Jugador.objects.filter(equipo__categoria__torneo_id=assigned_torneo)
    else:
        torneos = Torneo.objects.all()
        categorias = Categoria.objects.all()
        equipos = Equipo.objects.all()
        jugadores = Jugador.objects.all()
    
    context = {
        'torneos': torneos,
        'categorias': categorias,
        'equipos': equipos,
        'jugadores': jugadores
    }
    return render(request, 'torneos/admin/dashboard.html', context)

@login_required
@admin_torneo_required
def administrar_torneo(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    categorias = Categoria.objects.filter(torneo=torneo)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, assigned_torneo=torneo.id)
        if form.is_valid():
            categoria = form.save(commit=False)
            # Forzar el torneo a la instancia del administrador
            categoria.torneo = torneo
            categoria.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('administrar_torneo', torneo_id=torneo_id)
    else:
        form = CategoriaForm(assigned_torneo=torneo.id)
    
    context = {
        'torneo': torneo,
        'categorias': categorias,
        'form': form
    }
    return render(request, 'torneos/admin/administrar_torneo.html', context)

@admin_torneo_required
def integrar_nuevo_equipo(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = list(Equipo.objects.filter(categoria=categoria))
    total_equipos = len(equipos)
    if total_equipos < 2:
        messages.error(request, f"La categoría '{categoria.nombre}' necesita al menos 2 equipos.")
        return redirect('administrar_torneo', torneo_id=categoria.torneo.id)
    grupo, created = Grupo.objects.get_or_create(
        categoria=categoria,
        nombre="Grupo Único",
        defaults={'descripcion': 'Grupo principal de la categoría'}
    )
    partidos = list(Partido.objects.filter(grupo__categoria=categoria).order_by('jornada', 'id'))
    n = total_equipos
    equipos_existentes = equipos[:-1]  # Todos menos el nuevo
    nuevo_equipo = equipos[-1]
    if partidos and (n - 1) % 2 == 0 and n % 2 == 1:
        total_jornadas = n - 1
        for jornada in range(1, total_jornadas + 1):
            partidos_jornada = [p for p in partidos if p.jornada == jornada]
            equipos_en_jornada = set()
            partido_descanso = None
            for p in partidos_jornada:
                equipos_en_jornada.add(p.equipo_local)
                equipos_en_jornada.add(p.equipo_visitante)
                # Detectar partido de descanso (local == visitante)
                if p.equipo_local == p.equipo_visitante:
                    partido_descanso = p
            equipo_descanso = None
            for eq in equipos_existentes:
                if eq not in equipos_en_jornada:
                    equipo_descanso = eq
                    break
            # Eliminar partido de descanso si existe y no está jugado
            if partido_descanso and not partido_descanso.jugado:
                partido_descanso.delete()
            # Crear partido entre el nuevo equipo y el que descansaba
            if equipo_descanso is not None:
                    Partido.objects.create(
                        grupo=grupo,
                        jornada=jornada,
                        equipo_local=equipo_descanso,
                        equipo_visitante=nuevo_equipo,
                        ubicacion=None,
                        fecha=None
                    )
        messages.success(request, f"El nuevo equipo '{nuevo_equipo.nombre}' fue integrado correctamente enfrentando al equipo que descansaba en cada jornada. El número de partidos por jornada aumentó.")
        return redirect('administrar_torneo', torneo_id=categoria.torneo.id)
    else:
        messages.error(request, "La integración automática solo está disponible al pasar de par a impar y con calendario existente.")
        return redirect('administrar_torneo', torneo_id=categoria.torneo.id)
# Vista independiente para jugadores


@login_required
@user_passes_test(is_capitan)
def gestion_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    # Verificar que el usuario es capitán de este equipo
    if not hasattr(request.user, 'capitan') or request.user.capitan.equipo != equipo:
        messages.error(request, 'No tienes permisos para gestionar este equipo.')
        return redirect('index')
    
    jugadores = Jugador.objects.filter(equipo=equipo)
    
    if request.method == 'POST':
        form = JugadorForm(request.POST, request.FILES)
        if form.is_valid():
            jugador = form.save(commit=False)
            jugador.equipo = equipo
            jugador.save()
            messages.success(request, 'Jugador agregado exitosamente.')
            return redirect('gestion_equipo', equipo_id=equipo.id)
    else:
        form = JugadorForm()
    
    context = {
        'equipo': equipo,
        'jugadores': jugadores,
        'form': form
    }
    return render(request, 'torneos/capitan/gestion_equipo.html', context)

def eliminatorias_view(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    eliminatorias = Eliminatoria.objects.filter(categoria=categoria).order_by('orden')
    partidos_eliminatoria = PartidoEliminatoria.objects.filter(eliminatoria__categoria=categoria)
    
    # Estadísticas
    total_partidos = partidos_eliminatoria.count()
    partidos_jugados = partidos_eliminatoria.filter(jugado=True).count()
    total_goles = partidos_eliminatoria.aggregate(
        total=Sum('goles_local') + Sum('goles_visitante')
    )['total'] or 0
    equipos_activos = Equipo.objects.filter(categoria=categoria).count()
    
    # Estructurar datos para el bracket
    bracket_data = {}
    for eliminatoria in eliminatorias:
        bracket_data[eliminatoria.get_nombre_display()] = {
            'partidos': partidos_eliminatoria.filter(eliminatoria=eliminatoria),
            'orden': eliminatoria.orden
        }
    
    context = {
        'categoria': categoria,
        'bracket_data': bracket_data,
        'total_partidos': total_partidos,
        'partidos_jugados': partidos_jugados,
        'total_goles': total_goles,
        'equipos_activos': equipos_activos
    }
    return render(request, 'torneos/eliminatorias.html', context)

def goleadores_view(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    goleadores = Goleador.objects.filter(
        Q(partido__grupo__categoria=categoria) |
        Q(partido_eliminatoria__eliminatoria__categoria=categoria) |
        Q(categoria=categoria)
    )

    # Calcular estadísticas
    total_goles = sum(goleador.goles for goleador in goleadores)
    total_partidos = Partido.objects.filter(grupo__categoria=categoria, jugado=True).count()
    total_jugadores = Jugador.objects.filter(equipo__categoria=categoria).count()
    total_equipos = Equipo.objects.filter(categoria=categoria).count()

    # Agrupar por jugador
    ranking = {}
    for goleador in goleadores:
        jugador = goleador.jugador
        if jugador.id not in ranking:
            ranking[jugador.id] = {
                'jugador': jugador,
                'total_goles': 0,
                'partidos_con_goles': set(),
            }
        ranking[jugador.id]['total_goles'] += goleador.goles
        # Registrar partido donde anotó (puede venir de partido o partido_eliminatoria)
        pid = None
        if getattr(goleador, 'partido_id', None):
            pid = f"p_{goleador.partido_id}"
        elif getattr(goleador, 'partido_eliminatoria_id', None):
            pid = f"pe_{goleador.partido_eliminatoria_id}"
        # Solo agregar si tenemos un identificador de partido
        if pid:
            ranking[jugador.id]['partidos_con_goles'].add(pid)

    goleadores_data = []
    for data in ranking.values():
        # Partidos donde anotó
        partidos_con_goles = len(data.get('partidos_con_goles', []))
        jugador = data['jugador']
        # Partidos jugados por el jugador en esta categoría (participaciones)
        partidos_jugados = ParticipacionJugador.objects.filter(
            jugador=jugador,
            partido__grupo__categoria=categoria,
            partido__jugado=True
        ).values('partido').distinct().count()
        # Si no hay registro de participaciones, usar al menos los partidos en los que anotó
        partidos_reales = max(partidos_jugados, partidos_con_goles, 1)
        # Promedio de goles por partido del jugador (por sus partidos jugados)
        data['promedio_goles'] = round(data['total_goles'] / partidos_reales, 2)
        # Efectividad: porcentaje de partidos jugados en los que anotó al menos 1 gol
        data['porcentaje_efectividad'] = int(round((partidos_con_goles / partidos_reales) * 100))
        # Partidos jugados efectivos que usaremos en la tabla (al menos 1)
        data['partidos_jugados'] = partidos_reales
        goleadores_data.append(data)

    goleadores_data = sorted(goleadores_data, key=lambda x: -x['total_goles'])

    context = {
        'categoria': categoria,
        'goleadores_data': goleadores_data,
        'total_goles': total_goles,
        'total_partidos': total_partidos,
        'total_jugadores': total_jugadores,
        'total_equipos': total_equipos,
        'promedio_goles': round(total_goles / max(total_partidos, 1), 2) if goleadores_data else 0,
        'mejor_promedio': goleadores_data[0] if goleadores_data else None,
        'equipo_mas_goles': goleadores_data[0]['jugador'].equipo.nombre if goleadores_data else 'N/A',
        'max_goles_equipo': goleadores_data[0]['total_goles'] if goleadores_data else 0
    }
    return render(request, 'torneos/goleadores.html', context)
@login_required
@admin_torneo_required
def generar_calendario(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = list(Equipo.objects.filter(categoria=categoria))
    
    if len(equipos) < 2:
        messages.error(request, 'Se necesitan al menos 2 equipos para generar un calendario.')
        return redirect('administrar_torneo', torneo_id=categoria.torneo.id)

    if request.method == 'POST':
        # Algoritmo round-robin doble (ida y vuelta)
        n = len(equipos)
        equipos_rr = equipos.copy()
        if n % 2 == 1:
            equipos_rr.append(None)  # Equipo ficticio para números impares
            n += 1
        partidos_por_jornada = n // 2
        total_jornadas = n - 1
        grupo, created = Grupo.objects.get_or_create(
            categoria=categoria,
            nombre="Grupo Único",
            defaults={'descripcion': 'Grupo principal de la categoría'}
        )
        Partido.objects.filter(grupo__categoria=categoria).delete()
        # Ida (alternancia local/visitante por jornada)
        temp_equipos = equipos_rr.copy()
        for jornada in range(1, total_jornadas + 1):
            equipos_en_jornada = set()
            for i in range(partidos_por_jornada):
                if jornada % 2 == 1:
                    local = temp_equipos[i]
                    visitante = temp_equipos[n - 1 - i]
                else:
                    local = temp_equipos[n - 1 - i]
                    visitante = temp_equipos[i]
                if local is not None and visitante is not None:
                    Partido.objects.create(
                        grupo=grupo,
                        jornada=jornada,
                        equipo_local=local,
                        equipo_visitante=visitante,
                        fecha=None
                    )
                    equipos_en_jornada.add(local)
                    equipos_en_jornada.add(visitante)
            # Si hay equipo descanso (impar), agrégalo como partido especial
            if None in temp_equipos:
                equipo_descanso = [eq for eq in temp_equipos if eq not in equipos_en_jornada and eq is not None]
                if equipo_descanso:
                    eq_descansa = equipo_descanso[0]
                    Partido.objects.create(
                        grupo=grupo,
                        jornada=jornada,
                        equipo_local=eq_descansa,
                        equipo_visitante=eq_descansa,
                        ubicacion=None,
                        fecha=None
                    )
            temp_equipos = [temp_equipos[0]] + [temp_equipos[-1]] + temp_equipos[1:-1]
        # Vuelta (alternancia local/visitante por jornada, invertidos)
        temp_equipos = equipos_rr.copy()
        for jornada in range(1, total_jornadas + 1):
            equipos_en_jornada = set()
            for i in range(partidos_por_jornada):
                if jornada % 2 == 1:
                    local = temp_equipos[n - 1 - i]
                    visitante = temp_equipos[i]
                else:
                    local = temp_equipos[i]
                    visitante = temp_equipos[n - 1 - i]
                if local is not None and visitante is not None:
                    Partido.objects.create(
                        grupo=grupo,
                        jornada=total_jornadas + jornada,
                        equipo_local=local,
                        equipo_visitante=visitante,
                        fecha=None
                    )
                    equipos_en_jornada.add(local)
                    equipos_en_jornada.add(visitante)
            # Si hay equipo descanso (impar), agrégalo como partido especial
            if None in temp_equipos:
                equipo_descanso = [eq for eq in temp_equipos if eq not in equipos_en_jornada and eq is not None]
                if equipo_descanso:
                    eq_descansa = equipo_descanso[0]
                    Partido.objects.create(
                        grupo=grupo,
                        jornada=total_jornadas + jornada,
                        equipo_local=eq_descansa,
                        equipo_visitante=eq_descansa,
                        ubicacion=None,
                        fecha=None
                    )
            temp_equipos = [temp_equipos[0]] + [temp_equipos[-1]] + temp_equipos[1:-1]
        messages.success(request, f'Calendario (ida y vuelta) generado con {total_jornadas*2} jornadas.')
        return redirect('administrar_torneo', torneo_id=categoria.torneo.id)
    else:
        # Mostrar confirmación visual
        return render(request, 'torneos/confirmar_generar_calendario.html', {
            'categoria': categoria,
            'equipos': equipos
        })


# Vista independiente para tabla de posiciones
def tabla_posiciones_view(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = Equipo.objects.filter(categoria=categoria)
    # Partidos válidos para la tabla: jugados o con goles cargados (>0)
    partidos_validos = Partido.objects.filter(
        Q(equipo_local__categoria=categoria) | Q(equipo_visitante__categoria=categoria)
    ).filter(
        Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
    )
    for equipo in equipos:
        partidos_jugados_eq = partidos_validos.filter(
            Q(equipo_local=equipo) | Q(equipo_visitante=equipo)
        ).count()
        partidos_ganados = partidos_validos.filter(
            Q(equipo_local=equipo, goles_local__gt=F('goles_visitante')) |
            Q(equipo_visitante=equipo, goles_visitante__gt=F('goles_local'))
        ).count()
        partidos_empatados = partidos_validos.filter(
            Q(equipo_local=equipo, goles_local=F('goles_visitante')) |
            Q(equipo_visitante=equipo, goles_visitante=F('goles_local'))
        ).count()
        partidos_perdidos = partidos_jugados_eq - partidos_ganados - partidos_empatados
        goles_favor = partidos_validos.filter(
            Q(equipo_local=equipo)
        ).aggregate(total=Sum('goles_local'))['total'] or 0
        goles_favor += partidos_validos.filter(
            Q(equipo_visitante=equipo)
        ).aggregate(total=Sum('goles_visitante'))['total'] or 0
        goles_contra = partidos_validos.filter(
            Q(equipo_local=equipo)
        ).aggregate(total=Sum('goles_visitante'))['total'] or 0
        goles_contra += partidos_validos.filter(
            Q(equipo_visitante=equipo)
        ).aggregate(total=Sum('goles_local'))['total'] or 0
        diferencia_goles = goles_favor - goles_contra
        puntos = (partidos_ganados * 3) + partidos_empatados
        equipo.partidos_jugados = partidos_jugados_eq
        equipo.partidos_ganados = partidos_ganados
        equipo.partidos_empatados = partidos_empatados
        equipo.partidos_perdidos = partidos_perdidos
        equipo.goles_favor = goles_favor
        equipo.goles_contra = goles_contra
        equipo.diferencia_goles = diferencia_goles
        equipo.puntos = puntos
    equipos = sorted(equipos, key=lambda x: (-x.puntos, -x.diferencia_goles, -x.goles_favor))
    context = {
        'categoria': categoria,
        'equipos': equipos
    }
    return render(request, 'torneos/tabla_posiciones.html', context)

# Vista independiente para equipos
def equipos_view(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = Equipo.objects.filter(categoria=categoria)
    context = {
        'categoria': categoria,
        'equipos': equipos
    }
    return render(request, 'torneos/equipos.html', context)
    
    # Algoritmo round-robin para generar partidos
    n = len(equipos)
    if n % 2 == 1:
        equipos.append(None)  # Equipo ficticio para números impares
        n += 1
    
    partidos_por_jornada = n // 2
    total_jornadas = n - 1
    
    # Crear grupos si es necesario
    grupo, created = Grupo.objects.get_or_create(
        categoria=categoria,
        nombre="Grupo Único",
        defaults={'descripcion': 'Grupo principal de la categoría'}
    )
    
    # Eliminar partidos existentes para esta categoría
    Partido.objects.filter(grupo__categoria=categoria).delete()
    
    # Generar partidos
    for jornada in range(1, total_jornadas + 1):
        for i in range(partidos_por_jornada):
            local = equipos[i]
            visitante = equipos[n - 1 - i]
            
            if local is not None and visitante is not None:
                Partido.objects.create(
                    grupo=grupo,
                    jornada=jornada,
                    equipo_local=local,
                    equipo_visitante=visitante,
                    fecha=None
                )
        
        # Rotar equipos
        equipos.insert(1, equipos.pop())
    
    messages.success(request, f'Calendario generado con {total_jornadas} jornadas.')
    return redirect('administrar_torneo', torneo_id=categoria.torneo.id)

def jugador_detalle(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    participaciones = jugador.participaciones.select_related('partido').order_by('-partido__fecha')
    categoria = jugador.equipo.categoria if jugador.equipo else None
    context = {
        'jugador': jugador,
        'participaciones': participaciones,
        'categoria': categoria,
    }
    return render(request, 'torneos/jugador_detalle.html', context)


def partido_detalle(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    # Construir una lista única de jugadores que anotaron EN ESTE PARTIDO
    goles_map = {}

    # Entradas por jornada (registro detallado por partido)
    for gj in GoleadorJornada.objects.filter(partido=partido).select_related('goleador__jugador'):
        try:
            jugador = gj.goleador.jugador
        except Exception:
            jugador = None
        if not jugador:
            continue
        gid = jugador.id
        goles_map.setdefault(gid, {'jugador': jugador, 'goles': 0})
        goles_map[gid]['goles'] += (gj.goles or 0)

    # NOTA: ignoramos Goleador.goles (puede ser acumulado del torneo).
    # Nos basamos únicamente en GoleadorJornada para contar goles en este partido.

    # Filtrar solo jugadores con >0 goles y ordenar por goles desc
    goleadores = [v for v in goles_map.values() if v['goles'] and v['goles'] > 0]
    goleadores.sort(key=lambda x: (-x['goles'], x['jugador'].apellido or ''))

    # Determinar categoría del partido (por grupo si existe, si no por equipo)
    categoria = None
    try:
        if partido.grupo and getattr(partido.grupo, 'categoria', None):
            categoria = partido.grupo.categoria
    except Exception:
        categoria = None

    if not categoria:
        categoria = getattr(partido.equipo_local, 'categoria', None) or getattr(partido.equipo_visitante, 'categoria', None)

    torneo = getattr(categoria, 'torneo', None) if categoria else None

    context = {
        'partido': partido,
        'goleadores': goleadores,
        'categoria': categoria,
        'torneo': torneo,
    }
    return render(request, 'torneos/partido_detalle.html', context)
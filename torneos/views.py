# Vista independiente para jugadores
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
    ultimos_resultados = partidos.filter(jugado=True).order_by('-fecha')[:50]
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

@user_passes_test(lambda u: u.is_superuser)
def estadisticas_view(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = Equipo.objects.filter(categoria=categoria)
    partidos = Partido.objects.filter(
        Q(grupo__categoria=categoria) |
        Q(grupo=None, equipo_local__categoria=categoria) |
        Q(grupo=None, equipo_visitante__categoria=categoria)
    )
    proximos_partidos = partidos.filter(jugado=False).order_by('fecha')[:10]
    ultimos_resultados = partidos.filter(jugado=True).order_by('-fecha')[:10]
    total_partidos = partidos.count()
    partidos_jugados = partidos.filter(jugado=True).count()
    partidos_pendientes = partidos.filter(jugado=False).count()
    total_goles_local = partidos.filter(jugado=True).aggregate(Sum('goles_local'))['goles_local__sum'] or 0
    total_goles_visitante = partidos.filter(jugado=True).aggregate(Sum('goles_visitante'))['goles_visitante__sum'] or 0
    total_goles = total_goles_local + total_goles_visitante
    context = {
        'categoria': categoria,
        'equipos': equipos,
        'proximos_partidos': proximos_partidos,
        'ultimos_resultados': ultimos_resultados,
        'total_partidos': total_partidos,
        'partidos_jugados': partidos_jugados,
        'partidos_pendientes': partidos_pendientes,
        'total_goles': total_goles
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
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F
from .models import *
from .forms import *
import json
from datetime import datetime

def is_admin(user):
    return user.is_superuser

def is_capitan(user):
    return hasattr(user, 'capitan') and user.capitan.activo

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
    
    context = {
        'torneo': torneo,
        'categorias': categorias
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
    # Próximos enfrentamientos (no jugados)
    proximos_partidos = list(partidos.filter(jugado=False))
    # Ordenar: primero por fecha si existe, si no por jornada
    proximos_partidos.sort(key=lambda p: (p.fecha if p.fecha else datetime(9999, 12, 31), p.jornada))
    # Últimos resultados (jugados, ordenados por fecha más reciente)
    ultimos_resultados = partidos.filter(jugado=True).order_by('-fecha')[:10]
    # Estadísticas generales
    total_partidos = partidos.count()
    partidos_jugados = partidos.filter(jugado=True).count()
    partidos_pendientes = partidos.filter(jugado=False).count()
    total_goles_local = partidos.filter(jugado=True).aggregate(Sum('goles_local'))['goles_local__sum'] or 0
    total_goles_visitante = partidos.filter(jugado=True).aggregate(Sum('goles_visitante'))['goles_visitante__sum'] or 0
    total_goles = total_goles_local + total_goles_visitante
    # Obtener estadísticas de equipos
    for equipo in equipos:
        partidos_jugados_eq = Partido.objects.filter(
            Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
            jugado=True
        ).count()
        partidos_ganados = Partido.objects.filter(
            Q(equipo_local=equipo, goles_local__gt=F('goles_visitante'), jugado=True) |
            Q(equipo_visitante=equipo, goles_visitante__gt=F('goles_local'), jugado=True)
        ).count()
        partidos_empatados = Partido.objects.filter(
            Q(equipo_local=equipo, goles_local=F('goles_visitante'), jugado=True) |
            Q(equipo_visitante=equipo, goles_visitante=F('goles_local'), jugado=True)
        ).count()
        partidos_perdidos = partidos_jugados_eq - partidos_ganados - partidos_empatados
        goles_favor = Partido.objects.filter(
            Q(equipo_local=equipo, jugado=True)
        ).aggregate(total=Sum('goles_local'))['total'] or 0
        goles_favor += Partido.objects.filter(
            Q(equipo_visitante=equipo, jugado=True)
        ).aggregate(total=Sum('goles_visitante'))['total'] or 0
        goles_contra = Partido.objects.filter(
            Q(equipo_local=equipo, jugado=True)
        ).aggregate(total=Sum('goles_visitante'))['total'] or 0
        goles_contra += Partido.objects.filter(
            Q(equipo_visitante=equipo, jugado=True)
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
        'jornadas': jornadas
    }
    return render(request, 'torneos/categoria_detalle.html', context)
@login_required
@user_passes_test(is_admin)
def administracion_dashboard(request):
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
@user_passes_test(is_admin)
def administrar_torneo(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    categorias = Categoria.objects.filter(torneo=torneo)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.torneo = torneo
            categoria.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('administrar_torneo', torneo_id=torneo.id)
    else:
        form = CategoriaForm()
    
    context = {
        'torneo': torneo,
        'categorias': categorias,
        'form': form
    }
    return render(request, 'torneos/admin/administrar_torneo.html', context)

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
                'total_goles': 0
            }
        ranking[jugador.id]['total_goles'] += goleador.goles

    goleadores_data = []
    for data in ranking.values():
        data['promedio_goles'] = round(data['total_goles'] / max(total_partidos, 1), 2)
        data['porcentaje_efectividad'] = min(100, data['total_goles'] * 10)  # Simulado
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
@user_passes_test(is_admin)
def generar_calendario(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = list(Equipo.objects.filter(categoria=categoria))
    
    if len(equipos) < 2:
        messages.error(request, 'Se necesitan al menos 2 equipos para generar un calendario.')
        return redirect('administrar_torneo', torneo_id=categoria.torneo.id)


# Vista independiente para tabla de posiciones
def tabla_posiciones_view(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = Equipo.objects.filter(categoria=categoria)
    for equipo in equipos:
        partidos_jugados_eq = Partido.objects.filter(
            Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
            jugado=True
        ).count()
        partidos_ganados = Partido.objects.filter(
            Q(equipo_local=equipo, goles_local__gt=F('goles_visitante'), jugado=True) |
            Q(equipo_visitante=equipo, goles_visitante__gt=F('goles_local'), jugado=True)
        ).count()
        partidos_empatados = Partido.objects.filter(
            Q(equipo_local=equipo, goles_local=F('goles_visitante'), jugado=True) |
            Q(equipo_visitante=equipo, goles_visitante=F('goles_local'), jugado=True)
        ).count()
        partidos_perdidos = partidos_jugados_eq - partidos_ganados - partidos_empatados
        goles_favor = Partido.objects.filter(
            Q(equipo_local=equipo, jugado=True)
        ).aggregate(total=Sum('goles_local'))['total'] or 0
        goles_favor += Partido.objects.filter(
            Q(equipo_visitante=equipo, jugado=True)
        ).aggregate(total=Sum('goles_visitante'))['total'] or 0
        goles_contra = Partido.objects.filter(
            Q(equipo_local=equipo, jugado=True)
        ).aggregate(total=Sum('goles_visitante'))['total'] or 0
        goles_contra += Partido.objects.filter(
            Q(equipo_visitante=equipo, jugado=True)
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
                    fecha=datetime.now()  # Ajustar según necesidad
                )
        
        # Rotar equipos
        equipos.insert(1, equipos.pop())
    
    messages.success(request, f'Calendario generado con {total_jornadas} jornadas.')
    return redirect('administrar_torneo', torneo_id=categoria.torneo.id)
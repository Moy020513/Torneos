# Importar decoradores antes de usarlos
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
import os

# Definir is_admin antes de cualquier uso en decoradores
def is_admin(user):
    return user.is_superuser

# =================== ELIMINAR IMÁGENES HUÉRFANAS ===================
@login_required
@user_passes_test(is_admin)
def admin_eliminar_imagenes_huerfanas(request):
    # Carpeta media
    media_root = settings.MEDIA_ROOT
    eliminadas = []
    from .models import Jugador, Equipo, Torneo
    # Solo eliminar archivos huérfanos (no asociados en la base de datos)
    # Jugadores
    fotos_dir = os.path.join(settings.MEDIA_ROOT, 'jugadores/fotos')
    if os.path.exists(fotos_dir):
        for fname in os.listdir(fotos_dir):
            fpath = os.path.join(fotos_dir, fname)
            if os.path.isfile(fpath):
                if not Jugador.objects.filter(foto__endswith=f'jugadores/fotos/{fname}').exists():
                    os.remove(fpath)
                    eliminadas.append(f"Foto huérfana eliminada: {fpath}")
    # Equipos
    logos_dir = os.path.join(settings.MEDIA_ROOT, 'equipos/logos')
    if os.path.exists(logos_dir):
        for fname in os.listdir(logos_dir):
            fpath = os.path.join(logos_dir, fname)
            if os.path.isfile(fpath):
                if not Equipo.objects.filter(logo__endswith=f'equipos/logos/{fname}').exists():
                    os.remove(fpath)
                    eliminadas.append(f"Logo huérfano de equipo eliminado: {fpath}")
    # Torneos
    tlogos_dir = os.path.join(settings.MEDIA_ROOT, 'torneos/logos')
    if os.path.exists(tlogos_dir):
        for fname in os.listdir(tlogos_dir):
            fpath = os.path.join(tlogos_dir, fname)
            if os.path.isfile(fpath):
                if not Torneo.objects.filter(logo__endswith=f'torneos/logos/{fname}').exists():
                    os.remove(fpath)
                    eliminadas.append(f"Logo huérfano de torneo eliminado: {fpath}")

    # Buscar archivos huérfanos en el sistema de archivos que no estén en la base de datos
    # Jugadores
    fotos_dir = os.path.join(settings.MEDIA_ROOT, 'jugadores/fotos')
    if os.path.exists(fotos_dir):
        for fname in os.listdir(fotos_dir):
            fpath = os.path.join(fotos_dir, fname)
            if os.path.isfile(fpath):
                if not Jugador.objects.filter(foto__endswith=f'jugadores/fotos/{fname}').exists():
                    os.remove(fpath)
                    eliminadas.append(f"Foto huérfana eliminada: {fpath}")
    # Equipos
    logos_dir = os.path.join(settings.MEDIA_ROOT, 'equipos/logos')
    if os.path.exists(logos_dir):
        for fname in os.listdir(logos_dir):
            fpath = os.path.join(logos_dir, fname)
            if os.path.isfile(fpath):
                if not Equipo.objects.filter(logo__endswith=f'equipos/logos/{fname}').exists():
                    os.remove(fpath)
                    eliminadas.append(f"Logo huérfano de equipo eliminado: {fpath}")
    # Torneos
    tlogos_dir = os.path.join(settings.MEDIA_ROOT, 'torneos/logos')
    if os.path.exists(tlogos_dir):
        for fname in os.listdir(tlogos_dir):
            fpath = os.path.join(tlogos_dir, fname)
            if os.path.isfile(fpath):
                if not Torneo.objects.filter(logo__endswith=f'torneos/logos/{fname}').exists():
                    os.remove(fpath)
                    eliminadas.append(f"Logo huérfano de torneo eliminado: {fpath}")
    context = {'eliminadas': eliminadas}
    return render(request, 'admin/torneos/eliminar_imagenes_huerfanas.html', context)

# Definir is_admin antes de cualquier uso en decoradores
def is_admin(user):
    return user.is_superuser

from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import date, timedelta, datetime

@login_required
@user_passes_test(is_admin)
def admin_detalle_jugador(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    # Calcular edad
    if jugador.fecha_nacimiento:
        today = date.today()
        jugador.edad = today.year - jugador.fecha_nacimiento.year - ((today.month, today.day) < (jugador.fecha_nacimiento.month, jugador.fecha_nacimiento.day))
    else:
        jugador.edad = "N/A"
    # Participaciones y partidos jugados
    participaciones = ParticipacionJugador.objects.filter(jugador=jugador).select_related('partido').order_by('-partido__fecha')
    partidos_jugados = participaciones.count()
    context = {
        'jugador': jugador,
        'participaciones': participaciones,
        'partidos_jugados': partidos_jugados,
        'verificado_por': jugador.verificado_por,
        'fecha_verificacion': jugador.fecha_verificacion,
    }
    return render(request, 'admin/jugadores/detalle.html', context)

# =================== ELIMINAR PARTICIPACION ===================

from django.views.decorators.http import require_POST

@login_required
@user_passes_test(is_admin)
def admin_eliminar_participacion(request, participacion_id):
    try:
        participacion = ParticipacionJugador.objects.get(id=participacion_id)
    except ParticipacionJugador.DoesNotExist:
        # Si ya no existe, redirigir con mensaje amigable en lugar de 404
        messages.warning(request, 'La participación que intentas eliminar ya no existe.')
        return redirect('admin_participaciones')

    if request.method == 'POST':
        participacion.delete()
        messages.success(request, 'Participación eliminada exitosamente.')
        return redirect('admin_participaciones')

    context = {'participacion': participacion}
    return render(request, 'admin/participaciones/eliminar.html', context)

from django.contrib.auth.decorators import login_required, user_passes_test

# Definir is_admin antes de cualquier uso en decoradores
def is_admin(user):
    return user.is_superuser

# Vista para registrar participaciones múltiples
@login_required
@user_passes_test(is_admin)
def admin_crear_participaciones_multiples(request):
    equipo_id = request.GET.get('equipo') or request.POST.get('equipo')
    form = ParticipacionMultipleForm(request.POST or None, equipo_id=equipo_id)
    if request.method == 'POST' and form.is_valid():
        jugadores = form.cleaned_data['jugadores']
        partido = form.cleaned_data['partido']
        creadas = 0
        for jugador in jugadores:
            obj, created = ParticipacionJugador.objects.get_or_create(jugador=jugador, partido=partido)
            if created:
                creadas += 1
                # Si el partido ya está marcado como jugado, crear registro de goleador con 0 goles (si no existe)
                try:
                    from .models import Goleador, GoleadorJornada
                    if partido.jugado:
                        # Determinar categoría si el partido pertenece a un grupo
                        categoria = None
                        if getattr(partido, 'grupo', None) and getattr(partido.grupo, 'categoria', None):
                            categoria = partido.grupo.categoria
                        # Obtener o crear Goleador padre
                        goleador, gcreated = Goleador.objects.get_or_create(jugador=jugador, categoria=categoria, defaults={'goles': 0})
                        # Si no existe jornada para ese partido, crear con 0 goles
                        exists = GoleadorJornada.objects.filter(goleador=goleador, partido=partido).exists()
                        if not exists:
                            GoleadorJornada.objects.create(goleador=goleador, partido=partido, goles=0)
                            # actualizar total de goles en padre (suma de jornadas)
                            total = GoleadorJornada.objects.filter(goleador=goleador).aggregate(total=Sum('goles'))['total'] or 0
                            goleador.goles = total
                            goleador.save()
                except Exception:
                    # No bloquear flujo por errores no críticos al crear goleador inicial
                    pass
        messages.success(request, f'Se registraron {creadas} participaciones.')
        return redirect('admin_participaciones')
    context = {'form': form, 'action': 'Registrar múltiples', 'equipo_id': equipo_id}
    return render(request, 'admin/participaciones/form_multiple.html', context)

# ...existing code...
# =================== PARTICIPACIONES DE JUGADORES ===================
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

@login_required
@user_passes_test(is_admin)
def admin_participaciones(request):
    search = request.GET.get('search', '')
    participaciones = ParticipacionJugador.objects.select_related('jugador', 'partido').order_by('-fecha_creacion')
    if search:
        participaciones = participaciones.filter(
            Q(jugador__nombre__icontains=search) |
            Q(jugador__apellido__icontains=search) |
            Q(partido__equipo_local__nombre__icontains=search) |
            Q(partido__equipo_visitante__nombre__icontains=search)
        )
    paginator = Paginator(participaciones, 20)
    page_number = request.GET.get('page')
    participaciones_paginadas = paginator.get_page(page_number)
    context = {
        'participaciones': participaciones_paginadas,
        'search': search,
    }
    return render(request, 'admin/participaciones/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_participacion(request):
    if request.method == 'POST':
        form = ParticipacionJugadorForm(request.POST)
        if form.is_valid():
            participacion = form.save()
            # Si el partido ya está marcado como jugado, crear un registro de goleador padre y jornada con 0 goles
            try:
                partido = participacion.partido
                from .models import Goleador, GoleadorJornada
                if getattr(partido, 'jugado', False):
                    categoria = None
                    if getattr(partido, 'grupo', None) and getattr(partido.grupo, 'categoria', None):
                        categoria = partido.grupo.categoria
                    jugador = participacion.jugador
                    goleador, gcreated = Goleador.objects.get_or_create(jugador=jugador, categoria=categoria, defaults={'goles': 0})
                    exists = GoleadorJornada.objects.filter(goleador=goleador, partido=partido).exists()
                    if not exists:
                        GoleadorJornada.objects.create(goleador=goleador, partido=partido, goles=0)
                        total = GoleadorJornada.objects.filter(goleador=goleador).aggregate(total=Sum('goles'))['total'] or 0
                        goleador.goles = total
                        goleador.save()
            except Exception:
                pass
            messages.success(request, 'Participación registrada exitosamente.')
            return redirect('admin_participaciones')
    else:
        form = ParticipacionJugadorForm()
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/participaciones/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_participacion(request, participacion_id):
    participacion = get_object_or_404(ParticipacionJugador, id=participacion_id)
    if request.method == 'POST':
        form = ParticipacionJugadorForm(request.POST, instance=participacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Participación actualizada exitosamente.')
            return redirect('admin_participaciones')
    else:
        form = ParticipacionJugadorForm(instance=participacion)
    context = {
        'form': form,
        'participacion': participacion,
        'action': 'Editar',
    }
    return render(request, 'admin/participaciones/form.html', context)

# =================== HERRAMIENTAS ADMINISTRATIVAS ===================
# ...existing code...

@login_required
@user_passes_test(is_admin)
def admin_herramientas(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'marcar_jugados':
            # Marcar como jugados los partidos con resultado
            partidos_actualizados = Partido.objects.filter(
                jugado=False
            ).exclude(
                goles_local__isnull=True,
                goles_visitante__isnull=True
            ).exclude(
                goles_local=0,
                goles_visitante=0
            ).update(jugado=True)
            messages.success(request, f'Se marcaron {partidos_actualizados} partidos como jugados.')
        elif action == 'asignar_fechas':
            # Asignar fecha actual a partidos finalizados sin fecha
            from django.utils import timezone
            partidos_sin_fecha = Partido.objects.filter(
                Q(jugado=True) | 
                (Q(goles_local__gt=0) | Q(goles_visitante__gt=0)),
                fecha__isnull=True
            )
            fecha_default = timezone.now()
            partidos_actualizados = 0
            for partido in partidos_sin_fecha:
                partido.fecha = fecha_default
                partido.save()
                partidos_actualizados += 1
            messages.success(request, f'Se asignó fecha a {partidos_actualizados} partidos.')
        elif action == 'resetear_resultados':
            # Resetear resultados de partidos no jugados
            partidos_reseteados = Partido.objects.filter(
                jugado=False
            ).exclude(
                goles_local__isnull=True,
                goles_visitante__isnull=True
            ).exclude(
                goles_local=0,
                goles_visitante=0
            ).update(goles_local=0, goles_visitante=0)
            messages.success(request, f'Se resetearon los resultados de {partidos_reseteados} partidos.')
        return redirect('admin_herramientas')

    # Detectar inconsistencias en partidos
    partidos_sin_fecha_con_resultado = Partido.objects.filter(
        fecha__isnull=True
    ).exclude(
        goles_local__isnull=True,
        goles_visitante__isnull=True
    ).exclude(
        goles_local=0,
        goles_visitante=0
    )

    partidos_jugados_sin_fecha = Partido.objects.filter(
        jugado=True,
        fecha__isnull=True
    )

    partidos_con_resultado_no_jugados = Partido.objects.filter(
        jugado=False
    ).exclude(
        goles_local__isnull=True,
        goles_visitante__isnull=True
    ).exclude(
        goles_local=0,
        goles_visitante=0
    )

    context = {
        'partidos_sin_fecha_con_resultado': partidos_sin_fecha_con_resultado,
        'partidos_jugados_sin_fecha': partidos_jugados_sin_fecha,
        'partidos_con_resultado_no_jugados': partidos_con_resultado_no_jugados,
    }
    return render(request, 'admin/herramientas/index.html', context)



from .models import UbicacionCampo
from django.core.paginator import Paginator
from .forms import AdminFormMixin



@login_required
@user_passes_test(is_admin)
def admin_campos(request):
    search = request.GET.get('search', '')
    campos = UbicacionCampo.objects.all()
    if search:
        campos = campos.filter(nombre__icontains=search)
    paginator = Paginator(campos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'campos': page_obj,
        'search': search,
    }
    return render(request, 'admin/campos/listar.html', context)


from django import forms
class UbicacionCampoForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = UbicacionCampo
        fields = ['nombre', 'direccion', 'latitud', 'longitud']
        labels = {
            'nombre': 'Nombre del Campo',
            'direccion': 'Dirección',
            'latitud': 'Latitud',
            'longitud': 'Longitud',
        }
        widgets = {
            'latitud': forms.NumberInput(attrs={'step': 'any'}),
            'longitud': forms.NumberInput(attrs={'step': 'any'}),
        }

@login_required
@user_passes_test(is_admin)
def admin_crear_campo(request):
    if request.method == 'POST':
        form = UbicacionCampoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campo creado exitosamente.')
            return redirect('admin_campos')
    else:
        form = UbicacionCampoForm()
    context = {'form': form, 'action': 'Crear'}
    return render(request, 'admin/campos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_campo(request, campo_id):
    campo = get_object_or_404(UbicacionCampo, id=campo_id)
    if request.method == 'POST':
        form = UbicacionCampoForm(request.POST, instance=campo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campo actualizado exitosamente.')
            return redirect('admin_campos')
    else:
        form = UbicacionCampoForm(instance=campo)
    context = {'form': form, 'campo': campo, 'action': 'Editar'}
    return render(request, 'admin/campos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_campo(request, campo_id):
    campo = get_object_or_404(UbicacionCampo, id=campo_id)
    if request.method == 'POST':
        campo.delete()
        messages.success(request, 'Campo eliminado exitosamente.')
        return redirect('admin_campos')
    context = {'campo': campo}
    return render(request, 'admin/campos/eliminar.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F, Max
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import *
from .forms import *
import json
# ...existing code...
# =================== DASHBOARD ===================
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Estadísticas generales
    total_torneos = Torneo.objects.count()
    total_equipos = Equipo.objects.count()
    total_jugadores = Jugador.objects.count()
    total_partidos = Partido.objects.count()
    
    # Nuevas estadísticas
    total_grupos = Grupo.objects.count()
    total_usuarios = User.objects.count()
    total_capitanes = Capitan.objects.count()
    total_eliminatorias = Eliminatoria.objects.count()
    
    # Estadísticas de partidos eliminatoria
    total_partidos_eliminatoria = PartidoEliminatoria.objects.count()
    partidos_eliminatoria_jugados = PartidoEliminatoria.objects.filter(jugado=True).count()
    partidos_eliminatoria_pendientes = total_partidos_eliminatoria - partidos_eliminatoria_jugados
    porcentaje_eliminatorias_completadas = (partidos_eliminatoria_jugados / max(total_partidos_eliminatoria, 1)) * 100
    
    # Estadísticas de goleadores
    total_goleadores = Goleador.objects.count()
    total_goles_sistema = Goleador.objects.aggregate(total=Sum('goles'))['total'] or 0
    max_goleador = Goleador.objects.order_by('-goles').first()
    max_goles_jugador = max_goleador.goles if max_goleador else 0
    
    # Torneos recientes
    torneos_recientes = Torneo.objects.all().order_by('-fecha_creacion')[:5]
    
    # Partidos jugados
    partidos_jugados = Partido.objects.filter(
        Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
    ).count()
    
    # Porcentajes
    porcentaje_partidos_jugados = (partidos_jugados / max(total_partidos, 1)) * 100
    
    # Equipos completos (con al menos 8 jugadores)
    equipos_completos = 0
    for equipo in Equipo.objects.all():
        if equipo.jugador_set.count() >= 8:
            equipos_completos += 1
    
    porcentaje_equipos_completos = (equipos_completos / max(total_equipos, 1)) * 100
    
    # Usuarios activos (que han iniciado sesión en los últimos 30 días)
    hace_30_dias = timezone.now() - timedelta(days=30)
    usuarios_activos = User.objects.filter(last_login__gte=hace_30_dias).count()
    
    # Capitanes activos
    capitanes_activos = Capitan.objects.filter(activo=True).count()
    
    # Goles totales
    goles_totales = Partido.objects.filter(
        Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
    ).aggregate(
        total=Sum('goles_local') + Sum('goles_visitante')
    )['total'] or 0
    
    # Últimos resultados
    ultimos_resultados = Partido.objects.filter(
        Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)
    ).order_by('-fecha')[:10]
    
    # Administradores del sistema
    total_admins = User.objects.filter(is_staff=True).count()
    
    context = {
        'total_torneos': total_torneos,
        'total_equipos': total_equipos,
        'total_jugadores': total_jugadores,
        'total_partidos': total_partidos,
        'total_grupos': total_grupos,
        'total_usuarios': total_usuarios,
        'total_capitanes': total_capitanes,
        'total_eliminatorias': total_eliminatorias,
        'total_partidos_eliminatoria': total_partidos_eliminatoria,
        'partidos_eliminatoria_jugados': partidos_eliminatoria_jugados,
        'partidos_eliminatoria_pendientes': partidos_eliminatoria_pendientes,
        'porcentaje_eliminatorias_completadas': round(porcentaje_eliminatorias_completadas, 1),
        'total_goleadores': total_goleadores,
        'total_goles_sistema': total_goles_sistema,
        'max_goles_jugador': max_goles_jugador,
        'torneos_recientes': torneos_recientes,
        'partidos_jugados': partidos_jugados,
        'porcentaje_partidos_jugados': round(porcentaje_partidos_jugados, 1),
        'equipos_completos': equipos_completos,
        'porcentaje_equipos_completos': round(porcentaje_equipos_completos, 1),
        'usuarios_activos': usuarios_activos,
        'capitanes_activos': capitanes_activos,
        'total_admins': total_admins,
        'goles_totales': goles_totales,
        'ultimos_resultados': ultimos_resultados,
    }
    return render(request, 'admin/dashboard.html', context)

# =================== TORNEOS ===================
@login_required
@user_passes_test(is_admin)
def admin_torneos(request):
    # Anotar con el conteo de categorías
    torneos = Torneo.objects.annotate(
        num_categorias=Count('categoria')
    ).order_by('-fecha_creacion')
    
    # Búsqueda
    search = request.GET.get('search')
    if search:
        torneos = torneos.filter(
            Q(nombre__icontains=search) |
            Q(descripcion__icontains=search)
        )
    
    # Ordenamiento por categorías
    orden = request.GET.get('orden', '')
    if orden == 'mas_categorias':
        torneos = torneos.order_by('-num_categorias', '-fecha_creacion')
    elif orden == 'menos_categorias':
        torneos = torneos.order_by('num_categorias', '-fecha_creacion')
    
    # Paginación
    paginator = Paginator(torneos, 10)
    page_number = request.GET.get('page')
    torneos = paginator.get_page(page_number)
    
    context = {
        'torneos': torneos,
        'search': search,
        'orden': orden,
    }
    return render(request, 'admin/torneos/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_torneo(request):
    if request.method == 'POST':
        form = TorneoForm(request.POST, request.FILES)
        if form.is_valid():
            torneo = form.save(commit=False)
            torneo.creado_por = request.user
            torneo.save()
            messages.success(request, 'Torneo creado exitosamente.')
            return redirect('admin_torneos')
    else:
        form = TorneoForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/torneos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_torneo(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    # Calcular el total de equipos de todas las categorías de este torneo
    categorias = torneo.categoria_set.all()
    total_equipos = sum(c.equipo_set.count() for c in categorias)

    if request.method == 'POST':
        form = TorneoForm(request.POST, request.FILES, instance=torneo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Torneo actualizado exitosamente.')
            return redirect('admin_torneos')
    else:
        form = TorneoForm(instance=torneo)

    context = {
        'form': form,
        'torneo': torneo,
        'action': 'Editar',
        'total_equipos': total_equipos,
    }
    return render(request, 'admin/torneos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_torneo(request, torneo_id):
    torneo = get_object_or_404(Torneo, id=torneo_id)
    
    if request.method == 'POST':
        nombre_torneo = torneo.nombre
        torneo.delete()
        messages.success(request, f'Torneo "{nombre_torneo}" eliminado exitosamente.')
        return redirect('admin_torneos')
    
    context = {
        'torneo': torneo,
    }
    return render(request, 'admin/torneos/eliminar.html', context)

# =================== CATEGORÍAS ===================
from django import forms

class IntegrarEquipoForm(forms.Form):
    equipo_id = forms.ModelChoiceField(queryset=Equipo.objects.none(), label="Equipo a integrar")

    def __init__(self, categoria, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipo_id'].queryset = Equipo.objects.filter(categoria=categoria)

@login_required
@user_passes_test(is_admin)
def admin_integrar_equipo_calendario(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = Equipo.objects.filter(categoria=categoria)
    if not equipos.exists():
        messages.error(request, 'No hay equipos en la categoría para integrar.')
        return redirect('admin_categorias')

    if request.method == 'POST':
        form = IntegrarEquipoForm(categoria, request.POST)
        if form.is_valid():
            equipo = form.cleaned_data['equipo_id']
            # Lógica para integrar el equipo al calendario respetando jornadas jugadas y descansos
            # 1. Obtener partidos jugados y jornadas existentes
            partidos = Partido.objects.filter(grupo__categoria=categoria).order_by('jornada')
            jornadas_existentes = set(partidos.values_list('jornada', flat=True))
            # 2. Calcular jornadas jugadas y descansos
            jornadas_jugadas = set(partidos.filter(jugado=True).values_list('jornada', flat=True))
            # 3. Integrar el equipo solo en jornadas futuras y asignar descansos donde corresponda
            # (Ejemplo simple: solo agrega partidos en jornadas no jugadas)
            grupo, created = Grupo.objects.get_or_create(
                categoria=categoria,
                nombre="Grupo Único",
                defaults={'descripcion': 'Grupo principal de la categoría'}
            )
            partidos_creados = 0
            for jornada in sorted(jornadas_existentes):
                if jornada in jornadas_jugadas:
                    continue  # No modificar jornadas ya jugadas
                # Crear partidos contra todos los equipos existentes en esa jornada
                for rival in equipos.exclude(id=equipo.id):
                    Partido.objects.create(
                        grupo=grupo,
                        jornada=jornada,
                        equipo_local=equipo,
                        equipo_visitante=rival,
                        fecha=datetime.now()  # O asignar fecha lógica
                    )
                    partidos_creados += 1
            messages.success(request, f'Equipo integrado al calendario. Se crearon {partidos_creados} partidos en jornadas futuras.')
            return redirect('admin_categorias')
    else:
        form = IntegrarEquipoForm(categoria)

    context = {
        'form': form,
        'categoria': categoria,
        'equipos': equipos,
    }
    return render(request, 'admin/categorias/integrar_equipo.html', context)
@login_required
@user_passes_test(is_admin)
def admin_categorias(request):
    categorias = Categoria.objects.all().select_related('torneo').order_by('-id')
    
    # Filtros
    torneo_id = request.GET.get('torneo')
    search = request.GET.get('search')
    
    if torneo_id:
        categorias = categorias.filter(torneo_id=torneo_id)
    
    if search:
        categorias = categorias.filter(
            Q(nombre__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(torneo__nombre__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(categorias, 10)
    page_number = request.GET.get('page')
    categorias = paginator.get_page(page_number)
    
    # Para el filtro
    torneos = Torneo.objects.all()
    
    context = {
        'categorias': categorias,
        'torneos': torneos,
        'torneo_id': torneo_id,
        'search': search,
    }
    return render(request, 'admin/categorias/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('admin_categorias')
    else:
        form = CategoriaForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/categorias/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('admin_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria,
        'action': 'Editar',
    }
    return render(request, 'admin/categorias/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        nombre_categoria = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre_categoria}" eliminada exitosamente.')
        return redirect('admin_categorias')
    
    context = {
        'categoria': categoria,
    }
    return render(request, 'admin/categorias/eliminar.html', context)

# =================== EQUIPOS ===================
@login_required
@user_passes_test(is_admin)
def admin_equipos(request):
    equipos = Equipo.objects.all().select_related('categoria', 'categoria__torneo').order_by('-fecha_creacion')
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    torneo_id = request.GET.get('torneo')
    search = request.GET.get('search')
    
    if categoria_id:
        equipos = equipos.filter(categoria_id=categoria_id)
    elif torneo_id:
        equipos = equipos.filter(categoria__torneo_id=torneo_id)
    
    if search:
        equipos = equipos.filter(
            Q(nombre__icontains=search) |
            Q(categoria__nombre__icontains=search) |
            Q(categoria__torneo__nombre__icontains=search)
        )
    
    # Agregar datos de jugadores
    for equipo in equipos:
        equipo.total_jugadores = equipo.jugador_set.count()
    
    # Paginación
    paginator = Paginator(equipos, 10)
    page_number = request.GET.get('page')
    equipos = paginator.get_page(page_number)
    
    # Para filtros
    torneos = Torneo.objects.all()
    categorias = Categoria.objects.all()
    
    context = {
        'equipos': equipos,
        'torneos': torneos,
        'categorias': categorias,
        'categoria_id': categoria_id,
        'torneo_id': torneo_id,
        'search': search,
    }
    return render(request, 'admin/equipos/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_equipo(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo creado exitosamente.')
            return redirect('admin_equipos')
    else:
        form = EquipoForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/equipos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo actualizado exitosamente.')
            return redirect('admin_equipos')
    else:
        form = EquipoForm(instance=equipo)
    
    context = {
        'form': form,
        'equipo': equipo,
        'action': 'Editar',
    }
    return render(request, 'admin/equipos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    if request.method == 'POST':
        nombre_equipo = equipo.nombre
        equipo.delete()
        messages.success(request, f'Equipo "{nombre_equipo}" eliminado exitosamente.')
        return redirect('admin_equipos')
    
    context = {
        'equipo': equipo,
    }
    return render(request, 'admin/equipos/eliminar.html', context)

# =================== JUGADORES ===================
@login_required
@user_passes_test(is_admin)
def admin_jugadores(request):
    jugadores = Jugador.objects.all().select_related('equipo', 'equipo__categoria', 'equipo__categoria__torneo').order_by('-fecha_creacion')
    
    # Filtros
    equipo_id = request.GET.get('equipo')
    categoria_id = request.GET.get('categoria')
    search = request.GET.get('search')
    
    if equipo_id:
        jugadores = jugadores.filter(equipo_id=equipo_id)
    elif categoria_id:
        jugadores = jugadores.filter(equipo__categoria_id=categoria_id)
    
    if search:
        jugadores = jugadores.filter(
            Q(nombre__icontains=search) |
            Q(apellido__icontains=search) |
            Q(equipo__nombre__icontains=search)
        )
    
    # Calcular edad para cada jugador
    from datetime import date
    for jugador in jugadores:
        if jugador.fecha_nacimiento:
            today = date.today()
            jugador.edad = today.year - jugador.fecha_nacimiento.year - ((today.month, today.day) < (jugador.fecha_nacimiento.month, jugador.fecha_nacimiento.day))
        else:
            jugador.edad = "N/A"
    
    # Paginación
    paginator = Paginator(jugadores, 15)
    page_number = request.GET.get('page')
    jugadores = paginator.get_page(page_number)
    
    # Para filtros
    equipos = Equipo.objects.all()
    categorias = Categoria.objects.all()
    
    context = {
        'jugadores': jugadores,
        'equipos': equipos,
        'categorias': categorias,
        'equipo_id': equipo_id,
        'categoria_id': categoria_id,
        'search': search,
    }
    return render(request, 'admin/jugadores/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_jugador(request):
    if request.method == 'POST':
        form = JugadorForm(request.POST, request.FILES)
        if form.is_valid():
            jugador = form.save(commit=False)
            # Asegurar que los jugadores siempre se creen como activos
            jugador.activo = True
            # Si el admin marca verificado al crear, registrar auditoría
            if form.cleaned_data.get('verificado'):
                jugador.verificado_por = request.user
                jugador.fecha_verificacion = timezone.now()
            jugador.save()
            messages.success(request, 'Jugador creado exitosamente.')
            return redirect('admin_jugadores')
    else:
        form = JugadorForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/jugadores/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_jugador(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    
    if request.method == 'POST':
        form = JugadorForm(request.POST, request.FILES, instance=jugador)
        if form.is_valid():
            jugador = form.save(commit=False)
            # Mantener siempre activo
            jugador.activo = True
            # Actualizar auditoría de verificación según el checkbox
            if form.cleaned_data.get('verificado'):
                jugador.verificado_por = request.user
                jugador.fecha_verificacion = timezone.now()
            else:
                jugador.verificado_por = None
                jugador.fecha_verificacion = None
            jugador.save()
            messages.success(request, 'Jugador actualizado exitosamente.')
            return redirect('admin_jugadores')
    else:
        form = JugadorForm(instance=jugador)
    
    context = {
        'form': form,
        'jugador': jugador,
        'action': 'Editar',
    }
    return render(request, 'admin/jugadores/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_jugador(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    
    if request.method == 'POST':
        nombre_jugador = f"{jugador.nombre} {jugador.apellido}"
        jugador.delete()
        messages.success(request, f'Jugador "{nombre_jugador}" eliminado exitosamente.')
        return redirect('admin_jugadores')
    
    context = {
        'jugador': jugador,
    }
    return render(request, 'admin/jugadores/eliminar.html', context)

# =================== PARTIDOS ===================
@login_required
@user_passes_test(is_admin)
def admin_partidos(request):
    # Obtener parámetros de filtrado
    categoria_id = request.GET.get('categoria', '')
    estado = request.GET.get('estado', '')
    search = request.GET.get('search', '')
    jornada = request.GET.get('jornada', '')
    
    # Obtener todos los partidos ordenados por jornada ascendente (1, 2, 3...)
    partidos = Partido.objects.select_related(
        'equipo_local',
        'equipo_visitante',
        'grupo__categoria__torneo'
    ).order_by('jornada', 'fecha', 'id')
    
    # Filtrar por categoría
    if categoria_id:
        partidos = partidos.filter(grupo__categoria_id=categoria_id)
    
    # Filtrar por estado
    if estado == 'jugado':
        partidos = partidos.filter(jugado=True)
    elif estado == 'pendiente':
        partidos = partidos.filter(jugado=False)
    
    # Filtrar por jornada
    if jornada:
        partidos = partidos.filter(jornada=jornada)
    
    # Búsqueda por equipos
    if search:
        partidos = partidos.filter(
            Q(equipo_local__nombre__icontains=search) |
            Q(equipo_visitante__nombre__icontains=search)
        )
    
    # Obtener todas las categorías para el filtro
    categorias = Categoria.objects.select_related('torneo').all()
    
    # Obtener todas las jornadas disponibles (sin duplicados, ordenadas)
    jornadas = Partido.objects.values_list('jornada', flat=True).distinct().order_by('jornada')
    
    # Paginación
    paginator = Paginator(partidos, 20)  # 20 partidos por página
    page_number = request.GET.get('page')
    partidos_paginados = paginator.get_page(page_number)
    
    context = {
        'partidos': partidos_paginados,
        'categorias': categorias,
        'jornadas': jornadas,
        'categoria_id': categoria_id,
        'estado': estado,
        'search': search,
        'jornada': jornada,
    }

    return render(request, 'admin/partidos/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_partido(request):
    if request.method == 'POST':
        form = PartidoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partido creado exitosamente.')
            return redirect('admin_partidos')
    else:
        form = PartidoForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/partidos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    
    if request.method == 'POST':
        form = PartidoForm(request.POST, instance=partido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partido actualizado exitosamente.')
            return redirect('admin_partidos')
    else:
        form = PartidoForm(instance=partido)
    
    context = {
        'form': form,
        'partido': partido,
        'action': 'Editar',
    }
    return render(request, 'admin/partidos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    
    if request.method == 'POST':
        partido.delete()
        messages.success(request, 'Partido eliminado exitosamente.')
        return redirect('admin_partidos')
    
    context = {
        'partido': partido,
    }
    return render(request, 'admin/partidos/eliminar.html', context)

# =================== USUARIOS ===================
# =================== REPORTES ===================
@login_required
@user_passes_test(is_admin)
def admin_reportes(request):
    # Estadísticas generales para reportes
    context = {
        'total_torneos': Torneo.objects.count(),
        'total_equipos': Equipo.objects.count(),
        'total_jugadores': Jugador.objects.count(),
        'total_partidos': Partido.objects.count(),
        'partidos_jugados': Partido.objects.filter(Q(jugado=True) | Q(goles_local__gt=0) | Q(goles_visitante__gt=0)).count(),
        'goles_totales': Partido.objects.aggregate(total=Sum('goles_local') + Sum('goles_visitante'))['total'] or 0,
    }
    return render(request, 'admin/reportes/dashboard.html', context)

# =================== AJAX HELPERS ===================
@login_required
@user_passes_test(is_admin)
def get_categorias_ajax(request):
    torneo_id = request.GET.get('torneo_id')
    categorias = []
    if torneo_id:
        categorias_qs = Categoria.objects.filter(torneo_id=torneo_id).values('id', 'nombre')
        categorias = list(categorias_qs)
    return JsonResponse({'categorias': categorias})

@login_required
@user_passes_test(is_admin)
def get_equipos_ajax(request):
    categoria_id = request.GET.get('categoria_id')
    equipos = []
    if categoria_id:
        equipos_qs = Equipo.objects.filter(categoria_id=categoria_id).values('id', 'nombre')
        equipos = list(equipos_qs)
    return JsonResponse({'equipos': equipos})

# ========== GRUPOS ==========

@login_required
@user_passes_test(is_admin)
def admin_grupos(request):
    # Búsqueda y filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria')
    
    grupos = Grupo.objects.select_related('categoria', 'categoria__torneo').all()
    
    if search:
        grupos = grupos.filter(
            Q(nombre__icontains=search) |
            Q(categoria__nombre__icontains=search) |
            Q(categoria__torneo__nombre__icontains=search)
        )
    
    if categoria_id:
        grupos = grupos.filter(categoria_id=categoria_id)
    
    grupos = grupos.order_by('categoria__torneo__nombre', 'categoria__nombre', 'nombre')
    
    # Paginación
    paginator = Paginator(grupos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Para el filtro de categorías
    categorias = Categoria.objects.select_related('torneo').all().order_by('torneo__nombre', 'nombre')
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'categoria_id': categoria_id,
        'categorias': categorias,
        'total_grupos': grupos.count(),
    }
    return render(request, 'admin/grupos/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_grupo(request):
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupo creado exitosamente.')
            return redirect('admin_grupos')
    else:
        form = GrupoForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/grupos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    
    if request.method == 'POST':
        form = GrupoForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupo actualizado exitosamente.')
            return redirect('admin_grupos')
    else:
        form = GrupoForm(instance=grupo)
    
    context = {
        'form': form,
        'grupo': grupo,
        'action': 'Editar',
    }
    return render(request, 'admin/grupos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    
    if request.method == 'POST':
        nombre_grupo = grupo.nombre
        grupo.delete()
        messages.success(request, f'Grupo "{nombre_grupo}" eliminado exitosamente.')
        return redirect('admin_grupos')
    
    context = {
        'grupo': grupo,
    }
    return render(request, 'admin/grupos/eliminar.html', context)

# ========== USUARIOS ==========

@login_required
@user_passes_test(is_admin)
def admin_usuarios(request):
    # Búsqueda y filtros
    search = request.GET.get('search', '')
    is_staff = request.GET.get('is_staff')
    is_active = request.GET.get('is_active')
    
    usuarios = User.objects.all()
    
    if search:
        usuarios = usuarios.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    if is_staff:
        usuarios = usuarios.filter(is_staff=(is_staff == 'true'))
    
    if is_active:
        usuarios = usuarios.filter(is_active=(is_active == 'true'))
    
    usuarios = usuarios.order_by('-date_joined')
    
    # Agregar información de capitán
    for usuario in usuarios:
        try:
            usuario.capitan_info = usuario.capitan
        except:
            usuario.capitan_info = None
    
    # Paginación
    paginator = Paginator(usuarios, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'usuarios': page_obj,  # El template espera 'usuarios'
        'page_obj': page_obj,
        'search': search,
        'is_staff': is_staff,
        'is_active': is_active,
        'total_usuarios': User.objects.count(),  # Total real, no filtrado
        'total_admins': User.objects.filter(is_staff=True).count(),
        'total_capitanes': Capitan.objects.filter(activo=True).count(),
    }
    return render(request, 'admin/usuarios/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario "{user.username}" creado exitosamente.')
            return redirect('admin_usuarios')
    else:
        form = UsuarioForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/usuarios/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario "{user.username}" actualizado exitosamente.')
            return redirect('admin_usuarios')
    else:
        form = UsuarioEditForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'action': 'Editar',
    }
    return render(request, 'admin/usuarios/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    
    # No permitir eliminar superusuarios ni el usuario actual
    if usuario.is_superuser:
        messages.error(request, 'No se puede eliminar un superusuario.')
        return redirect('admin_usuarios')
    
    if usuario == request.user:
        messages.error(request, 'No puedes eliminarte a ti mismo.')
        return redirect('admin_usuarios')
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{username}" eliminado exitosamente.')
        return redirect('admin_usuarios')
    
    context = {
        'usuario': usuario,
    }
    return render(request, 'admin/usuarios/eliminar.html', context)

# ========== CAPITANES ==========

@login_required
@user_passes_test(is_admin)
def admin_capitanes(request):
    # Búsqueda y filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria')
    activo = request.GET.get('activo')
    
    capitanes = Capitan.objects.select_related('usuario', 'equipo', 'equipo__categoria').all()
    
    if search:
        capitanes = capitanes.filter(
            Q(usuario__username__icontains=search) |
            Q(usuario__first_name__icontains=search) |
            Q(usuario__last_name__icontains=search) |
            Q(equipo__nombre__icontains=search)
        )
    
    if categoria_id:
        capitanes = capitanes.filter(equipo__categoria_id=categoria_id)
    
    if activo:
        capitanes = capitanes.filter(activo=(activo == 'true'))
    
    capitanes = capitanes.order_by('equipo__categoria__nombre', 'equipo__nombre')
    
    # Paginación
    paginator = Paginator(capitanes, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Para filtros
    categorias = Categoria.objects.select_related('torneo').all().order_by('torneo__nombre', 'nombre')
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'categoria_id': categoria_id,
        'activo': activo,
        'categorias': categorias,
        'total_capitanes': capitanes.count(),
        'capitanes_activos': Capitan.objects.filter(activo=True).count(),
    }
    return render(request, 'admin/capitanes/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_capitan(request):
    if request.method == 'POST':
        form = CapitanForm(request.POST)
        if form.is_valid():
            capitan = form.save()
            messages.success(request, f'Capitán "{capitan.usuario.username}" asignado exitosamente.')
            return redirect('admin_capitanes')
    else:
        form = CapitanForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/capitanes/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_capitan(request, capitan_id):
    capitan = get_object_or_404(Capitan, id=capitan_id)
    
    if request.method == 'POST':
        form = CapitanForm(request.POST, instance=capitan)
        if form.is_valid():
            capitan = form.save()
            messages.success(request, f'Capitán "{capitan.usuario.username}" actualizado exitosamente.')
            return redirect('admin_capitanes')
    else:
        form = CapitanForm(instance=capitan)
    
    context = {
        'form': form,
        'capitan': capitan,
        'action': 'Editar',
    }
    return render(request, 'admin/capitanes/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_capitan(request, capitan_id):
    capitan = get_object_or_404(Capitan, id=capitan_id)
    
    if request.method == 'POST':
        usuario_nombre = capitan.usuario.username
        capitan.delete()
        messages.success(request, f'Capitán "{usuario_nombre}" removido exitosamente.')
        return redirect('admin_capitanes')
    
    context = {
        'capitan': capitan,
    }
    return render(request, 'admin/capitanes/eliminar.html', context)

# ========== ELIMINATORIAS ==========

@login_required
@user_passes_test(is_admin)
def admin_eliminatorias(request):
    # Búsqueda y filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria')
    
    eliminatorias = Eliminatoria.objects.select_related('categoria', 'categoria__torneo').all()
    
    if search:
        eliminatorias = eliminatorias.filter(
            Q(nombre__icontains=search) |
            Q(categoria__nombre__icontains=search) |
            Q(categoria__torneo__nombre__icontains=search)
        )
    
    if categoria_id:
        eliminatorias = eliminatorias.filter(categoria_id=categoria_id)
    
    eliminatorias = eliminatorias.order_by('categoria__torneo__nombre', 'categoria__nombre', 'orden')
    
    # Agregar información de partidos para cada eliminatoria
    for eliminatoria in eliminatorias:
        eliminatoria.partidos_count = PartidoEliminatoria.objects.filter(eliminatoria=eliminatoria).count()
        eliminatoria.partidos_jugados = PartidoEliminatoria.objects.filter(eliminatoria=eliminatoria, jugado=True).count()
    
    # Paginación
    paginator = Paginator(eliminatorias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Para filtros
    categorias = Categoria.objects.select_related('torneo').all().order_by('torneo__nombre', 'nombre')
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'categoria_id': categoria_id,
        'categorias': categorias,
        'total_eliminatorias': eliminatorias.count(),
    }
    return render(request, 'admin/eliminatorias/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_eliminatoria(request):
    if request.method == 'POST':
        form = EliminatoriaForm(request.POST)
        if form.is_valid():
            eliminatoria = form.save()
            messages.success(request, f'Eliminatoria "{eliminatoria.get_nombre_display()}" creada exitosamente.')
            return redirect('admin_eliminatorias')
    else:
        form = EliminatoriaForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/eliminatorias/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_eliminatoria(request, eliminatoria_id):
    eliminatoria = get_object_or_404(Eliminatoria, id=eliminatoria_id)
    
    if request.method == 'POST':
        form = EliminatoriaForm(request.POST, instance=eliminatoria)
        if form.is_valid():
            eliminatoria = form.save()
            messages.success(request, f'Eliminatoria "{eliminatoria.get_nombre_display()}" actualizada exitosamente.')
            return redirect('admin_eliminatorias')
    else:
        form = EliminatoriaForm(instance=eliminatoria)
    
    context = {
        'form': form,
        'eliminatoria': eliminatoria,
        'action': 'Editar',
    }
    return render(request, 'admin/eliminatorias/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_eliminatoria(request, eliminatoria_id):
    eliminatoria = get_object_or_404(Eliminatoria, id=eliminatoria_id)
    
    if request.method == 'POST':
        nombre_eliminatoria = eliminatoria.get_nombre_display()
        eliminatoria.delete()
        messages.success(request, f'Eliminatoria "{nombre_eliminatoria}" eliminada exitosamente.')
        return redirect('admin_eliminatorias')
    
    context = {
        'eliminatoria': eliminatoria,
    }
    return render(request, 'admin/eliminatorias/eliminar.html', context)

# ========== PARTIDOS DE ELIMINATORIA ==========

@login_required
@user_passes_test(is_admin)
def admin_partidos_eliminatoria(request):
    # Búsqueda y filtros
    search = request.GET.get('search', '')
    eliminatoria_id = request.GET.get('eliminatoria')
    jugado = request.GET.get('jugado')
    
    partidos = PartidoEliminatoria.objects.select_related(
        'eliminatoria', 'eliminatoria__categoria', 'eliminatoria__categoria__torneo',
        'equipo_local', 'equipo_visitante'
    ).all()
    
    if search:
        partidos = partidos.filter(
            Q(equipo_local__nombre__icontains=search) |
            Q(equipo_visitante__nombre__icontains=search) |
            Q(eliminatoria__categoria__nombre__icontains=search) |
            Q(eliminatoria__categoria__torneo__nombre__icontains=search)
        )
    
    if eliminatoria_id:
        partidos = partidos.filter(eliminatoria_id=eliminatoria_id)
    
    if jugado:
        partidos = partidos.filter(jugado=(jugado == 'true'))
    
    partidos = partidos.order_by('eliminatoria__orden', 'fecha')
    
    # Paginación
    paginator = Paginator(partidos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Para filtros
    eliminatorias = Eliminatoria.objects.select_related('categoria', 'categoria__torneo').all().order_by('categoria__torneo__nombre', 'categoria__nombre', 'orden')
    
    # Estadísticas
    total_partidos_eliminatoria = PartidoEliminatoria.objects.count()
    partidos_jugados = PartidoEliminatoria.objects.filter(jugado=True).count()
    partidos_pendientes = total_partidos_eliminatoria - partidos_jugados
    eliminatorias_count = Eliminatoria.objects.count()
    
    context = {
        'partidos': page_obj,  # Cambiar para que coincida con el template
        'page_obj': page_obj,
        'search': search,
        'eliminatoria_id': eliminatoria_id,
        'jugado': jugado,
        'eliminatorias': eliminatorias,
        'total_partidos': total_partidos_eliminatoria,
        'partidos_jugados': partidos_jugados,
        'partidos_pendientes': partidos_pendientes,
        'eliminatorias_count': eliminatorias_count,
    }
    return render(request, 'admin/partidos_eliminatoria/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_partido_eliminatoria(request):
    if request.method == 'POST':
        form = PartidoEliminatoriaForm(request.POST)
        if form.is_valid():
            partido = form.save()
            messages.success(request, f'Partido de eliminatoria creado exitosamente.')
            return redirect('admin_partidos_eliminatoria')
    else:
        form = PartidoEliminatoriaForm()
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/partidos_eliminatoria/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_partido_eliminatoria(request, partido_id):
    partido = get_object_or_404(PartidoEliminatoria, id=partido_id)
    
    if request.method == 'POST':
        form = PartidoEliminatoriaForm(request.POST, instance=partido)
        if form.is_valid():
            partido = form.save()
            messages.success(request, f'Partido de eliminatoria actualizado exitosamente.')
            return redirect('admin_partidos_eliminatoria')
    else:
        form = PartidoEliminatoriaForm(instance=partido)
    
    context = {
        'form': form,
        'partido': partido,
        'action': 'Editar',
    }
    return render(request, 'admin/partidos_eliminatoria/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_partido_eliminatoria(request, partido_id):
    partido = get_object_or_404(PartidoEliminatoria, id=partido_id)
    
    if request.method == 'POST':
        descripcion_partido = f"{partido.equipo_local} vs {partido.equipo_visitante}"
        partido.delete()
        messages.success(request, f'Partido de eliminatoria "{descripcion_partido}" eliminado exitosamente.')
        return redirect('admin_partidos_eliminatoria')
    
    context = {
        'partido': partido,
    }
    return render(request, 'admin/partidos_eliminatoria/eliminar.html', context)

# =================== GOLEADORES ===================
@login_required
@user_passes_test(is_admin)
def admin_goleadores(request):
    # Búsqueda y filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria')
    equipo_id = request.GET.get('equipo')
    min_goles = request.GET.get('min_goles')
    
    goleadores = Goleador.objects.select_related(
        'jugador', 'jugador__equipo', 'categoria', 'partido', 'partido_eliminatoria'
    ).all()
    
    if search:
        goleadores = goleadores.filter(
            Q(jugador__nombre__icontains=search) |
            Q(jugador__equipo__nombre__icontains=search) |
            Q(categoria__nombre__icontains=search)
        )
    
    if categoria_id:
        goleadores = goleadores.filter(categoria_id=categoria_id)
    
    if equipo_id:
        goleadores = goleadores.filter(jugador__equipo_id=equipo_id)
    
    if min_goles:
        try:
            goleadores = goleadores.filter(goles__gte=int(min_goles))
        except ValueError:
            pass
    
    goleadores = goleadores.order_by('-goles', 'jugador__nombre')
    
    # Paginación
    paginator = Paginator(goleadores, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Para filtros
    categorias = Categoria.objects.select_related('torneo').all().order_by('torneo__nombre', 'nombre')
    equipos = Equipo.objects.all().order_by('nombre')
    
    # Estadísticas
    total_goleadores = Goleador.objects.count()
    total_goles_anotados = Goleador.objects.aggregate(total=Sum('goles'))['total'] or 0
    max_goles = goleadores.aggregate(max_goles=Max('goles'))['max_goles'] or 0
    categorias_count = Goleador.objects.values('categoria').distinct().count()
    
    context = {
        'goleadores': page_obj,
        'page_obj': page_obj,
        'search': search,
        'categoria_id': categoria_id,
        'equipo_id': equipo_id,
        'min_goles': min_goles,
        'categorias': categorias,
        'equipos': equipos,
        'total_goleadores': total_goleadores,
        'total_goles_anotados': total_goles_anotados,
        'max_goles': max_goles,
        'categorias_count': categorias_count,
    }
    return render(request, 'admin/goleadores/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_goleador(request):
    # Ahora mantendremos un único Goleador y varias entradas tipo "jornada" relacionadas
    partidos = Partido.objects.all().order_by('jornada', 'fecha')
    partidos_elim = PartidoEliminatoria.objects.all().order_by('eliminatoria__orden', 'fecha')

    if request.method == 'POST':
        partido_list = request.POST.getlist('partido')
        partido_elim_list = request.POST.getlist('partido_eliminatoria')
        goles_list = request.POST.getlist('goles')

        jugador_id = request.POST.get('jugador')
        categoria_id = request.POST.get('categoria')

        if not jugador_id or not categoria_id:
            messages.error(request, 'Debe seleccionar jugador y categoría.')
            form = GoleadorForm(request.POST)
        else:
            jugador = get_object_or_404(Jugador, id=jugador_id)
            categoria = get_object_or_404(Categoria, id=categoria_id)

            # Primero validar que la suma de goles por partido no exceda el resultado oficial
            partidos_sum = {}
            partidos_elim_sum = {}
            for i in range(len(goles_list)):
                try:
                    g = int(goles_list[i])
                except (ValueError, TypeError):
                    continue
                p = partido_list[i] if i < len(partido_list) else ''
                pe = partido_elim_list[i] if i < len(partido_elim_list) else ''
                if p and not pe:
                    partidos_sum[p] = partidos_sum.get(p, 0) + g
                elif pe and not p:
                    partidos_elim_sum[pe] = partidos_elim_sum.get(pe, 0) + g

            errors = []
            from .models import GoleadorJornada
            # Validar partidos regulares
            for pid, sum_g in partidos_sum.items():
                partido = Partido.objects.filter(id=pid).first()
                if not partido:
                    errors.append(f'Partido con id {pid} no encontrado.')
                    continue
                partido_total = (partido.goles_local or 0) + (partido.goles_visitante or 0)
                existing_total = GoleadorJornada.objects.filter(partido=partido).aggregate(total=Sum('goles'))['total'] or 0
                proposed_total = existing_total + sum_g
                if proposed_total > partido_total:
                    errors.append(f'El total de goles para el partido {partido.equipo_local} vs {partido.equipo_visitante} sería {proposed_total} — el resultado oficial es {partido_total}. Ajusta las jornadas.')

            # Validar partidos de eliminatoria
            for peid, sum_g in partidos_elim_sum.items():
                partido_elim = PartidoEliminatoria.objects.filter(id=peid).first()
                if not partido_elim:
                    errors.append(f'Partido de eliminatoria con id {peid} no encontrado.')
                    continue
                partido_total = (partido_elim.goles_local or 0) + (partido_elim.goles_visitante or 0)
                existing_total = GoleadorJornada.objects.filter(partido_eliminatoria=partido_elim).aggregate(total=Sum('goles'))['total'] or 0
                proposed_total = existing_total + sum_g
                if proposed_total > partido_total:
                    errors.append(f'El total de goles para el partido {partido_elim.equipo_local} vs {partido_elim.equipo_visitante} sería {proposed_total} — el resultado oficial es {partido_total}. Ajusta las jornadas.')

            if errors:
                for err in errors:
                    messages.error(request, err)
                form = GoleadorForm(request.POST)
            else:
                # Crear un único registro Goleador
                goleador = Goleador.objects.create(jugador=jugador, categoria=categoria, goles=0)

                created = 0
                total_goles = 0
                for i in range(len(goles_list)):
                    try:
                        g = int(goles_list[i])
                    except (ValueError, TypeError):
                        continue
                    p = partido_list[i] if i < len(partido_list) else ''
                    pe = partido_elim_list[i] if i < len(partido_elim_list) else ''
                    if p and not pe:
                        partido = Partido.objects.filter(id=p).first()
                        if partido:
                            GoleadorJornada.objects.create(goleador=goleador, partido=partido, goles=g)
                            created += 1
                            total_goles += g
                    elif pe and not p:
                        partido_elim = PartidoEliminatoria.objects.filter(id=pe).first()
                        if partido_elim:
                            GoleadorJornada.objects.create(goleador=goleador, partido_eliminatoria=partido_elim, goles=g)
                            created += 1
                            total_goles += g

                # Actualizar total de goles en el registro padre
                goleador.goles = total_goles
                goleador.save()

                if created:
                    messages.success(request, f'Se crearon {created} jornada(s) para el goleador.')
                    return redirect('admin_goleadores')
    else:
        form = GoleadorForm()

    context = {
        'form': form,
        'action': 'Crear',
        'partidos': partidos,
        'partidos_elim': partidos_elim,
        'jugadores': Jugador.objects.select_related('equipo').all().order_by('nombre'),
    }
    return render(request, 'admin/goleadores/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_goleador(request, goleador_id):
    goleador = get_object_or_404(Goleador, id=goleador_id)
    partidos = Partido.objects.all().order_by('jornada', 'fecha')
    partidos_elim = PartidoEliminatoria.objects.all().order_by('eliminatoria__orden', 'fecha')

    if request.method == 'POST':
        partido_list = request.POST.getlist('partido')
        partido_elim_list = request.POST.getlist('partido_eliminatoria')
        goles_list = request.POST.getlist('goles')

        # Si no vienen listas, fallback al form tradicional
        if not goles_list:
            form = GoleadorForm(request.POST, instance=goleador)
            if form.is_valid():
                goleador = form.save()
                messages.success(request, f'Goleador "{goleador.jugador.nombre}" actualizado exitosamente.')
                return redirect('admin_goleadores')
        else:
            # Rebuild/validate form to update jugador/categoria si vienen en POST
            form = GoleadorForm(request.POST, instance=goleador)
            if form.is_valid():
                goleador = form.save(commit=False)
                # Primero validar que la suma de goles por partido no exceda el resultado oficial
                partidos_sum = {}
                partidos_elim_sum = {}
                for i in range(len(goles_list)):
                    try:
                        g = int(goles_list[i])
                    except (ValueError, TypeError):
                        continue
                    p = partido_list[i] if i < len(partido_list) else ''
                    pe = partido_elim_list[i] if i < len(partido_elim_list) else ''
                    if p and not pe:
                        partidos_sum[p] = partidos_sum.get(p, 0) + g
                    elif pe and not p:
                        partidos_elim_sum[pe] = partidos_elim_sum.get(pe, 0) + g

                errors = []
                from .models import GoleadorJornada
                # Validar partidos regulares (excluir contribuciones del goleador actual)
                for pid, sum_g in partidos_sum.items():
                    partido = Partido.objects.filter(id=pid).first()
                    if not partido:
                        errors.append(f'Partido con id {pid} no encontrado.')
                        continue
                    partido_total = (partido.goles_local or 0) + (partido.goles_visitante or 0)
                    existing_total = GoleadorJornada.objects.filter(partido=partido).exclude(goleador=goleador).aggregate(total=Sum('goles'))['total'] or 0
                    proposed_total = existing_total + sum_g
                    if proposed_total > partido_total:
                        errors.append(f'El total de goles para el partido {partido.equipo_local} vs {partido.equipo_visitante} sería {proposed_total} — el resultado oficial es {partido_total}. Ajusta las jornadas.')

                # Validar partidos de eliminatoria
                for peid, sum_g in partidos_elim_sum.items():
                    partido_elim = PartidoEliminatoria.objects.filter(id=peid).first()
                    if not partido_elim:
                        errors.append(f'Partido de eliminatoria con id {peid} no encontrado.')
                        continue
                    partido_total = (partido_elim.goles_local or 0) + (partido_elim.goles_visitante or 0)
                    existing_total = GoleadorJornada.objects.filter(partido_eliminatoria=partido_elim).exclude(goleador=goleador).aggregate(total=Sum('goles'))['total'] or 0
                    proposed_total = existing_total + sum_g
                    if proposed_total > partido_total:
                        errors.append(f'El total de goles para el partido {partido_elim.equipo_local} vs {partido_elim.equipo_visitante} sería {proposed_total} — el resultado oficial es {partido_total}. Ajusta las jornadas.')

                if errors:
                    for err in errors:
                        messages.error(request, err)
                    # fall through to render with errors
                else:
                    # Eliminamos jornadas previas y recreamos según las filas del formulario
                    GoleadorJornada.objects.filter(goleador=goleador).delete()

                    total_goles = 0
                    created = 0
                    for i in range(len(goles_list)):
                        try:
                            g = int(goles_list[i])
                        except (ValueError, TypeError):
                            continue
                        p = partido_list[i] if i < len(partido_list) else ''
                        pe = partido_elim_list[i] if i < len(partido_elim_list) else ''
                        if p and not pe:
                            partido = Partido.objects.filter(id=p).first()
                            if partido:
                                GoleadorJornada.objects.create(goleador=goleador, partido=partido, goles=g)
                                total_goles += g
                                created += 1
                        elif pe and not p:
                            partido_elim = PartidoEliminatoria.objects.filter(id=pe).first()
                            if partido_elim:
                                GoleadorJornada.objects.create(goleador=goleador, partido_eliminatoria=partido_elim, goles=g)
                                total_goles += g
                                created += 1

                    goleador.goles = total_goles
                    goleador.save()

                    messages.success(request, f'Goleador "{goleador.jugador.nombre}" actualizado exitosamente.')
                    return redirect('admin_goleadores')
            # si form no válido, se mostrará con errores
    else:
        form = GoleadorForm(instance=goleador)

    context = {
        'form': form,
        'goleador': goleador,
        'action': 'Editar',
        'partidos': partidos,
        'partidos_elim': partidos_elim,
        'jugadores': Jugador.objects.select_related('equipo').all().order_by('nombre'),
    }
    return render(request, 'admin/goleadores/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_goleador(request, goleador_id):
    goleador = get_object_or_404(Goleador, id=goleador_id)
    
    if request.method == 'POST':
        jugador_nombre = goleador.jugador.nombre
        goles = goleador.goles
        goleador.delete()
        messages.success(request, f'Registro de goleador "{jugador_nombre}" ({goles} goles) eliminado exitosamente.')
        return redirect('admin_goleadores')
    
    context = {
        'goleador': goleador,
    }
    return render(request, 'admin/goleadores/eliminar.html', context)


# =================== CAMPOS (UBICACIONCAMPO) ===================
from .forms import AdminFormMixin
from django import forms

class UbicacionCampoForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = UbicacionCampo
        fields = ['nombre', 'direccion', 'latitud', 'longitud']
        labels = {
            'nombre': 'Nombre del Campo',
            'direccion': 'Dirección',
            'latitud': 'Latitud',
            'longitud': 'Longitud',
        }

@login_required
@user_passes_test(is_admin)
def admin_campos(request):
    search = request.GET.get('search', '')
    campos = UbicacionCampo.objects.all()
    if search:
        campos = campos.filter(nombre__icontains=search)
    paginator = Paginator(campos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'campos': page_obj,
        'search': search,
    }
    return render(request, 'admin/campos/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_campo(request):
    if request.method == 'POST':
        form = UbicacionCampoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campo creado exitosamente.')
            return redirect('admin_campos')
    else:
        form = UbicacionCampoForm()
    context = {'form': form, 'action': 'Crear'}
    return render(request, 'admin/campos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_campo(request, campo_id):
    campo = get_object_or_404(UbicacionCampo, id=campo_id)
    if request.method == 'POST':
        form = UbicacionCampoForm(request.POST, instance=campo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campo actualizado exitosamente.')
            return redirect('admin_campos')
    else:
        form = UbicacionCampoForm(instance=campo)
    context = {'form': form, 'campo': campo, 'action': 'Editar'}
    return render(request, 'admin/campos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_campo(request, campo_id):
    campo = get_object_or_404(UbicacionCampo, id=campo_id)
    if request.method == 'POST':
        campo.delete()
        messages.success(request, 'Campo eliminado exitosamente.')
        return redirect('admin_campos')
    context = {'campo': campo}
    return render(request, 'admin/campos/eliminar.html', context)

    if request.method == 'POST':
        if action == 'marcar_jugados':
            # Marcar como jugados los partidos con resultado
            partidos_actualizados = Partido.objects.filter(
                jugado=False
            ).exclude(
                goles_local__isnull=True,
                goles_visitante__isnull=True
            ).exclude(
                goles_local=0,
                goles_visitante=0
            ).update(jugado=True)
            messages.success(request, f'Se marcaron {partidos_actualizados} partidos como jugados.')
        elif action == 'asignar_fechas':
            # Asignar fecha actual a partidos finalizados sin fecha
            from django.utils import timezone
            partidos_sin_fecha = Partido.objects.filter(
                Q(jugado=True) | 
                (Q(goles_local__gt=0) | Q(goles_visitante__gt=0)),
                fecha__isnull=True
            )
            fecha_default = timezone.now()
            partidos_actualizados = 0
            for partido in partidos_sin_fecha:
                partido.fecha = fecha_default
                partido.save()
                partidos_actualizados += 1
            messages.success(request, f'Se asignó fecha a {partidos_actualizados} partidos.')
        elif action == 'resetear_resultados':
            # Resetear resultados de partidos no jugados
            partidos_reseteados = Partido.objects.filter(
                jugado=False
            ).exclude(
                goles_local__isnull=True,
                goles_visitante__isnull=True
            ).exclude(
                goles_local=0,
                goles_visitante=0
            ).update(goles_local=0, goles_visitante=0)
            messages.success(request, f'Se resetearon los resultados de {partidos_reseteados} partidos.')
        return redirect('admin_herramientas')

@login_required
@user_passes_test(is_admin)
def admin_generar_calendario(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    equipos = list(Equipo.objects.filter(categoria=categoria))
    if len(equipos) < 2:
        messages.error(request, 'Se necesitan al menos 2 equipos para generar un calendario.')
        return redirect('admin_categorias')

    if request.method == 'POST':
        tipo = request.POST.get('tipo_calendario')
        if tipo not in ['ida', 'ida_vuelta']:
            messages.error(request, 'Debes seleccionar el tipo de calendario.')
            return redirect('admin_generar_calendario', categoria_id=categoria.id)
        n = len(equipos)
        equipos_rr = equipos.copy()
        if n % 2 == 1:
            equipos_rr.append(None)
            n += 1
        partidos_por_jornada = n // 2
        total_jornadas = n - 1
        grupo, created = Grupo.objects.get_or_create(
            categoria=categoria,
            nombre="Grupo Único",
            defaults={'descripcion': 'Grupo principal de la categoría'}
        )
        Partido.objects.filter(grupo__categoria=categoria).delete()
        total = 0
        # Ida
        for jornada in range(1, total_jornadas + 1):
            for i in range(partidos_por_jornada):
                local = equipos_rr[i]
                visitante = equipos_rr[n - 1 - i]
                if local is not None and visitante is not None:
                    Partido.objects.create(
                        grupo=grupo,
                        jornada=jornada,
                        equipo_local=local,
                        equipo_visitante=visitante,
                        ubicacion=None
                    )
                    total += 1
            equipos_rr.insert(1, equipos_rr.pop())
        # Vuelta si corresponde
        if tipo == 'ida_vuelta':
            equipos_rr = equipos.copy()
            if n % 2 == 1:
                equipos_rr.append(None)
            for jornada in range(1, total_jornadas + 1):
                for i in range(partidos_por_jornada):
                    local = equipos_rr[n - 1 - i]
                    visitante = equipos_rr[i]
                    if local is not None and visitante is not None:
                        Partido.objects.create(
                            grupo=grupo,
                            jornada=total_jornadas + jornada,
                            equipo_local=local,
                            equipo_visitante=visitante,
                            ubicacion=None
                        )
                        total += 1
                equipos_rr.insert(1, equipos_rr.pop())
        messages.success(request, f'Calendario generado para "{categoria.nombre}" ({"ida y vuelta" if tipo=="ida_vuelta" else "solo ida"}). Total partidos: {total}.')
        return redirect('admin_categorias')
    else:
        return render(request, 'torneos/confirmar_generar_calendario.html', {
            'categoria': categoria,
            'equipos': equipos
        })
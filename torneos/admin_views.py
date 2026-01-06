# Importar decoradores antes de usarlos
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
import os

# is_admin: permite acceso a superusuarios del sistema y a los
# usuarios que hayan sido marcados como AdministradorTorneo (instancia)
from .models import AdministradorTorneo, Arbitro

def is_admin(user):
    try:
        if user and getattr(user, 'is_superuser', False):
            return True
        # Usuarios asignados como administrador de torneo pueden acceder
        return AdministradorTorneo.objects.filter(usuario=user, activo=True).exists()
    except Exception:
        return False


def get_assigned_torneo_id(user):
    """Devuelve el id del torneo asignado al AdministradorTorneo activo del usuario, o None."""
    try:
        at = AdministradorTorneo.objects.filter(usuario=user, activo=True).values_list('torneo_id', flat=True).first()
        return at
    except Exception:
        return None


def registrar_actividad(torneo, usuario, tipo_accion, tipo_modelo, descripcion, objeto_id=None, request=None):
    """Helper para registrar actividades en el sistema."""
    from .models import RegistroActividad
    try:
        ip_address = None
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
        
        RegistroActividad.objects.create(
            torneo=torneo,
            usuario=usuario,
            tipo_accion=tipo_accion,
            tipo_modelo=tipo_modelo,
            descripcion=descripcion,
            objeto_id=objeto_id,
            ip_address=ip_address
        )
    except Exception as e:
        # No fallar si el registro de actividad falla
        print(f"Error registrando actividad: {e}")


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

# Reusar la implementación de is_admin definida arriba
# (evitamos redefinirlo accidentalmente)

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

# Reusar la implementación de is_admin definida arriba
# (evitamos redefinirlo accidentalmente)

# Vista para registrar participaciones múltiples
@login_required
@user_passes_test(is_admin)
def admin_crear_participaciones_multiples(request):
    equipo_id = request.GET.get('equipo') or request.POST.get('equipo')
    # Limitar equipos si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    form = ParticipacionMultipleForm(request.POST or None, equipo_id=equipo_id, assigned_torneo=assigned_torneo)
    if request.method == 'POST' and form.is_valid():
        jugadores = form.cleaned_data['jugadores']
        partido = form.cleaned_data['partido']
        equipo = form.cleaned_data.get('equipo')
        # Validación servidor-side: asegurar que el equipo pertenece al torneo asignado
        if assigned_torneo and equipo and not request.user.is_superuser:
            if equipo.categoria.torneo_id != assigned_torneo:
                messages.error(request, 'No puedes registrar participaciones para un equipo de otro torneo.')
                context = {'form': form, 'action': 'Registrar múltiples', 'equipo_id': equipo_id}
                return render(request, 'admin/participaciones/form_multiple.html', context)
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
    # Preparar lista de jugadores ordenada para la plantilla (mejor control de orden)
    jugadores_list = []
    if equipo_id:
        try:
            jugadores_list = list(Jugador.objects.filter(equipo_id=equipo_id).order_by('nombre', 'apellido'))
        except Exception:
            jugadores_list = []

    context = {'form': form, 'action': 'Registrar múltiples', 'equipo_id': equipo_id, 'jugadores_list': jugadores_list}
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
    # Si el usuario es AdministradorTorneo, limitar a las participaciones de partidos del torneo asignado
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            participaciones = participaciones.filter(
                Q(partido__grupo__categoria__torneo_id=assigned_torneo) |
                Q(partido__equipo_local__categoria__torneo_id=assigned_torneo) |
                Q(partido__equipo_visitante__categoria__torneo_id=assigned_torneo)
            )
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
    # Si el usuario es AdministradorTorneo, mostrar solo campos asociados a partidos del torneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if assigned_torneo:
        campos = UbicacionCampo.objects.filter(
            Q(partidos__grupo__categoria__torneo_id=assigned_torneo) |
            Q(partidos__equipo_local__categoria__torneo_id=assigned_torneo) |
            Q(partidos__equipo_visitante__categoria__torneo_id=assigned_torneo) |
            Q(creado_por=request.user)
        ).distinct()
    else:
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
            campo = form.save(commit=False)
            campo.creado_por = request.user
            campo.save()
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
from django.http import JsonResponse, HttpResponseForbidden
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
    # Si el usuario es AdministradorTorneo, limitar estadísticas a su torneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    # Estadísticas generales (filtradas si aplica)
    if assigned_torneo:
        total_torneos = Torneo.objects.filter(id=assigned_torneo).count()
        total_equipos = Equipo.objects.filter(categoria__torneo_id=assigned_torneo).count()
        total_jugadores = Jugador.objects.filter(equipo__categoria__torneo_id=assigned_torneo).count()
        total_partidos = Partido.objects.filter(Q(grupo__categoria__torneo_id=assigned_torneo) | Q(grupo=None, equipo_local__categoria__torneo_id=assigned_torneo) | Q(grupo=None, equipo_visitante__categoria__torneo_id=assigned_torneo)).count()
    else:
        total_torneos = Torneo.objects.count()
        total_equipos = Equipo.objects.count()
        total_jugadores = Jugador.objects.count()
        total_partidos = Partido.objects.count()
    
    # Nuevas estadísticas
    total_grupos = Grupo.objects.count()
    total_usuarios = User.objects.count()
    total_representantees = Representante.objects.count()
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
    if assigned_torneo:
        equipos_iter = Equipo.objects.filter(categoria__torneo_id=assigned_torneo)
    else:
        equipos_iter = Equipo.objects.all()

    for equipo in equipos_iter:
        if equipo.jugador_set.count() >= 8:
            equipos_completos += 1
    
    porcentaje_equipos_completos = (equipos_completos / max(total_equipos, 1)) * 100
    
    # Usuarios activos (que han iniciado sesión en los últimos 30 días)
    hace_30_dias = timezone.now() - timedelta(days=30)
    usuarios_activos = User.objects.filter(last_login__gte=hace_30_dias).count()
    
    # Representantees activos
    representantees_activos = Representante.objects.filter(activo=True).count()
    
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

    # Actividades recientes
    actividades_recientes_qs = RegistroActividad.objects.select_related('usuario', 'torneo')
    if assigned_torneo:
        actividades_recientes_qs = actividades_recientes_qs.filter(torneo_id=assigned_torneo)
    actividades_recientes = actividades_recientes_qs.order_by('-fecha_hora')[:5]
    
    context = {
        'total_torneos': total_torneos,
        'total_equipos': total_equipos,
        'total_jugadores': total_jugadores,
        'total_partidos': total_partidos,
        'total_grupos': total_grupos,
        'total_usuarios': total_usuarios,
        'total_representantees': total_representantees,
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
        'representantees_activos': representantees_activos,
        'total_admins': total_admins,
        'goles_totales': goles_totales,
        'ultimos_resultados': ultimos_resultados,
        'actividades_recientes': actividades_recientes,
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
    # Si es admin de torneo, solo puede editar el torneo asignado
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if not assigned_torneo or assigned_torneo != torneo_id:
            return HttpResponseForbidden('No tienes permiso para editar este torneo.')

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
    # Si el usuario es un AdministradorTorneo, limitar a su torneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            categorias = categorias.filter(torneo_id=assigned_torneo)
    
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
    
    # Para el filtro: si es admin de torneo, solo incluir su torneo
    if assigned_torneo:
        torneos = Torneo.objects.filter(id=assigned_torneo)
    else:
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
    # Si el usuario es AdministradorTorneo, obtener su torneo asignado y pasarlo al formulario
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, assigned_torneo=assigned_torneo)
        if form.is_valid():
            # Si hay torneo asignado, forzar ese valor antes de guardar porque el campo puede venir deshabilitado
            if assigned_torneo and not request.user.is_superuser:
                categoria = form.save(commit=False)
                categoria.torneo_id = assigned_torneo
                categoria.save()
            else:
                form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('admin_categorias')
    else:
        form = CategoriaForm(assigned_torneo=assigned_torneo)
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/categorias/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    # Si el usuario es AdministradorTorneo, obtener su torneo asignado
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria, assigned_torneo=assigned_torneo)
        if form.is_valid():
            if assigned_torneo and not request.user.is_superuser:
                categoria_obj = form.save(commit=False)
                categoria_obj.torneo_id = assigned_torneo
                categoria_obj.save()
            else:
                form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('admin_categorias')
    else:
        form = CategoriaForm(instance=categoria, assigned_torneo=assigned_torneo)
    
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
    # Limitar por torneo si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            equipos = equipos.filter(categoria__torneo_id=assigned_torneo)
    
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
    
    # Para filtros: si es admin de torneo, limitar opciones
    if assigned_torneo:
        torneos = Torneo.objects.filter(id=assigned_torneo)
        categorias = Categoria.objects.filter(torneo_id=assigned_torneo)
    else:
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
    # Limitar categorías si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, assigned_torneo=assigned_torneo)
        if form.is_valid():
            # Validar que la categoría pertenezca al torneo asignado si aplica
            if assigned_torneo and not request.user.is_superuser:
                categoria = form.cleaned_data.get('categoria')
                if categoria and categoria.torneo_id != assigned_torneo:
                    messages.error(request, 'No puedes crear un equipo en una categoría de otro torneo.')
                else:
                    equipo = form.save()
                    
                    # Registrar actividad
                    registrar_actividad(
                        torneo=equipo.categoria.torneo,
                        usuario=request.user,
                        tipo_accion='crear',
                        tipo_modelo='equipo',
                        descripcion=f"Equipo creado: {equipo.nombre} en {equipo.categoria.nombre}",
                        objeto_id=equipo.id,
                        request=request
                    )
                    
                    messages.success(request, 'Equipo creado exitosamente.')
                    return redirect('admin_equipos')
            else:
                equipo = form.save()
                
                # Registrar actividad
                registrar_actividad(
                    torneo=equipo.categoria.torneo,
                    usuario=request.user,
                    tipo_accion='crear',
                    tipo_modelo='equipo',
                    descripcion=f"Equipo creado: {equipo.nombre} en {equipo.categoria.nombre}",
                    objeto_id=equipo.id,
                    request=request
                )
                
                messages.success(request, 'Equipo creado exitosamente.')
                return redirect('admin_equipos')
    else:
        form = EquipoForm(assigned_torneo=assigned_torneo)
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/equipos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    # Limitar categorías si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo, assigned_torneo=assigned_torneo)
        if form.is_valid():
            if assigned_torneo and not request.user.is_superuser:
                categoria = form.cleaned_data.get('categoria')
                if categoria and categoria.torneo_id != assigned_torneo:
                    messages.error(request, 'No puedes asignar una categoría de otro torneo.')
                else:
                    equipo = form.save()
                    
                    # Registrar actividad
                    registrar_actividad(
                        torneo=equipo.categoria.torneo,
                        usuario=request.user,
                        tipo_accion='modificar',
                        tipo_modelo='equipo',
                        descripcion=f"Equipo modificado: {equipo.nombre} en {equipo.categoria.nombre}",
                        objeto_id=equipo.id,
                        request=request
                    )
                    
                    messages.success(request, 'Equipo actualizado exitosamente.')
                    return redirect('admin_equipos')
            else:
                equipo = form.save()
                
                # Registrar actividad
                registrar_actividad(
                    torneo=equipo.categoria.torneo,
                    usuario=request.user,
                    tipo_accion='modificar',
                    tipo_modelo='equipo',
                    descripcion=f"Equipo modificado: {equipo.nombre} en {equipo.categoria.nombre}",
                    objeto_id=equipo.id,
                    request=request
                )
                
                messages.success(request, 'Equipo actualizado exitosamente.')
                return redirect('admin_equipos')
    else:
        form = EquipoForm(instance=equipo, assigned_torneo=assigned_torneo)
    
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
    # Limitar por torneo si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            jugadores = jugadores.filter(equipo__categoria__torneo_id=assigned_torneo)
    
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
    
    # Para filtros (limitar si es admin de torneo)
    if assigned_torneo:
        equipos = Equipo.objects.filter(categoria__torneo_id=assigned_torneo)
        categorias = Categoria.objects.filter(torneo_id=assigned_torneo)
    else:
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
    # Limitar equipos si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if request.method == 'POST':
        form = JugadorForm(request.POST, request.FILES, assigned_torneo=assigned_torneo)
        if form.is_valid():
            # Validar que el equipo pertenezca al torneo asignado si aplica
            equipo = form.cleaned_data.get('equipo')
            if assigned_torneo and not request.user.is_superuser and equipo and equipo.categoria.torneo_id != assigned_torneo:
                messages.error(request, 'No puedes crear un jugador en un equipo de otro torneo.')
            else:
                jugador = form.save(commit=False)
                # Asegurar que los jugadores siempre se creen como activos
                jugador.activo = True
                # Si el admin marca verificado al crear, registrar auditoría
                if form.cleaned_data.get('verificado'):
                    jugador.verificado_por = request.user
                    jugador.fecha_verificacion = timezone.now()
                jugador.save()
                
                # Registrar actividad
                torneo = jugador.equipo.categoria.torneo if jugador.equipo else None
                if torneo:
                    registrar_actividad(
                        torneo=torneo,
                        usuario=request.user,
                        tipo_accion='crear',
                        tipo_modelo='jugador',
                        descripcion=f"Jugador creado: {jugador.nombre} {jugador.apellido} ({jugador.equipo.nombre if jugador.equipo else 'Sin equipo'})",
                        objeto_id=jugador.id,
                        request=request
                    )
                
                messages.success(request, 'Jugador creado exitosamente.')
                return redirect('admin_jugadores')
    else:
        form = JugadorForm(assigned_torneo=assigned_torneo)
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/jugadores/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_jugador(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id)
    # Limitar equipos si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if request.method == 'POST':
        form = JugadorForm(request.POST, request.FILES, instance=jugador, assigned_torneo=assigned_torneo)
        if form.is_valid():
            equipo = form.cleaned_data.get('equipo')
            if assigned_torneo and not request.user.is_superuser and equipo and equipo.categoria.torneo_id != assigned_torneo:
                messages.error(request, 'No puedes asignar un jugador a un equipo de otro torneo.')
            else:
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
                
                # Registrar actividad
                torneo = jugador.equipo.categoria.torneo if jugador.equipo else None
                if torneo:
                    registrar_actividad(
                        torneo=torneo,
                        usuario=request.user,
                        tipo_accion='modificar',
                        tipo_modelo='jugador',
                        descripcion=f"Jugador modificado: {jugador.nombre} {jugador.apellido} ({jugador.equipo.nombre if jugador.equipo else 'Sin equipo'})",
                        objeto_id=jugador.id,
                        request=request
                    )
                
                messages.success(request, 'Jugador actualizado exitosamente.')
                return redirect('admin_jugadores')
    else:
        form = JugadorForm(instance=jugador, assigned_torneo=assigned_torneo)
    
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
        torneo = jugador.equipo.categoria.torneo if jugador.equipo else None
        equipo_nombre = jugador.equipo.nombre if jugador.equipo else 'Sin equipo'
        jugador_id = jugador.id
        
        jugador.delete()
        
        # Registrar actividad
        if torneo:
            registrar_actividad(
                torneo=torneo,
                usuario=request.user,
                tipo_accion='eliminar',
                tipo_modelo='jugador',
                descripcion=f"Jugador eliminado: {nombre_jugador} ({equipo_nombre})",
                objeto_id=jugador_id,
                request=request
            )
        
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
    arbitro_id = request.GET.get('arbitro', '')
    
    # Obtener todos los partidos ordenados por jornada ascendente (1, 2, 3...)
    partidos = Partido.objects.select_related(
        'equipo_local',
        'equipo_visitante',
        'grupo__categoria__torneo',
        'arbitro__usuario'
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

    # Filtrar por árbitro
    if arbitro_id:
        partidos = partidos.filter(arbitro_id=arbitro_id)
    
    # Búsqueda por equipos
    if search:
        partidos = partidos.filter(
            Q(equipo_local__nombre__icontains=search) |
            Q(equipo_visitante__nombre__icontains=search)
        )
    
    # Limitar por torneo si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            partidos = partidos.filter(grupo__categoria__torneo_id=assigned_torneo)

    # Obtener todas las categorías para el filtro (limitadas si aplica)
    if assigned_torneo:
        categorias = Categoria.objects.select_related('torneo').filter(torneo_id=assigned_torneo)
        arbitros = Arbitro.objects.select_related('usuario').filter(torneo_id=assigned_torneo)
    else:
        categorias = Categoria.objects.select_related('torneo').all()
        arbitros = Arbitro.objects.select_related('usuario', 'torneo').all()
    
    # Obtener todas las jornadas disponibles (sin duplicados, ordenadas) — considerar filtro aplicado
    jornadas_qs = partidos.values_list('jornada', flat=True).distinct().order_by('jornada')
    jornadas = jornadas_qs
    
    # Paginación
    paginator = Paginator(partidos, 20)  # 20 partidos por página
    page_number = request.GET.get('page')
    partidos_paginados = paginator.get_page(page_number)
    
    context = {
        'partidos': partidos_paginados,
        'categorias': categorias,
        'arbitros': arbitros,
        'jornadas': jornadas,
        'categoria_id': categoria_id,
        'estado': estado,
        'search': search,
        'jornada': jornada,
        'arbitro_id': arbitro_id,
    }

    return render(request, 'admin/partidos/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_partido(request):
    # Limitar grupos y equipos si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if request.method == 'POST':
        form = PartidoForm(request.POST, assigned_torneo=assigned_torneo, current_user=request.user)
        if form.is_valid():
            # Validaciones servidor-side: asegurar que los equipos y grupo pertenezcan al torneo asignado
            if assigned_torneo and not request.user.is_superuser:
                grupo = form.cleaned_data.get('grupo')
                equipo_local = form.cleaned_data.get('equipo_local')
                equipo_visitante = form.cleaned_data.get('equipo_visitante')
                arbitro = form.cleaned_data.get('arbitro')
                invalid = False
                if grupo and grupo.categoria.torneo_id != assigned_torneo:
                    invalid = True
                if equipo_local and equipo_local.categoria.torneo_id != assigned_torneo:
                    invalid = True
                if equipo_visitante and equipo_visitante.categoria.torneo_id != assigned_torneo:
                    invalid = True
                if arbitro and arbitro.torneo_id != assigned_torneo:
                    invalid = True
                if invalid:
                    messages.error(request, 'No puedes crear un partido con equipos o grupo de otro torneo.')
                    context = {'form': form, 'action': 'Crear'}
                    return render(request, 'admin/partidos/form.html', context)
                # Validar ubicacion (si se seleccionó) pertenece al torneo
                ubicacion = form.cleaned_data.get('ubicacion')
                if ubicacion:
                    try:
                        from .models import UbicacionCampo
                        if not UbicacionCampo.objects.filter(id=ubicacion.id).filter(
                            Q(partidos__grupo__categoria__torneo_id=assigned_torneo) |
                            Q(partidos__equipo_local__categoria__torneo_id=assigned_torneo) |
                            Q(partidos__equipo_visitante__categoria__torneo_id=assigned_torneo) |
                            Q(creado_por=request.user)
                        ).exists():
                            messages.error(request, 'La ubicación seleccionada no está asociada a tu torneo.')
                            context = {'form': form, 'action': 'Crear'}
                            return render(request, 'admin/partidos/form.html', context)
                    except Exception:
                        pass
            form.save()
            messages.success(request, 'Partido creado exitosamente.')
            return redirect('admin_partidos')
    else:
        form = PartidoForm(assigned_torneo=assigned_torneo, current_user=request.user)
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/partidos/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    # Limitar grupos y equipos si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if request.method == 'POST':
        form = PartidoForm(request.POST, instance=partido, assigned_torneo=assigned_torneo, current_user=request.user)
        if form.is_valid():
            if assigned_torneo and not request.user.is_superuser:
                grupo = form.cleaned_data.get('grupo')
                equipo_local = form.cleaned_data.get('equipo_local')
                equipo_visitante = form.cleaned_data.get('equipo_visitante')
                arbitro = form.cleaned_data.get('arbitro')
                invalid = False
                if grupo and grupo.categoria.torneo_id != assigned_torneo:
                    invalid = True
                if equipo_local and equipo_local.categoria.torneo_id != assigned_torneo:
                    invalid = True
                if equipo_visitante and equipo_visitante.categoria.torneo_id != assigned_torneo:
                    invalid = True
                if arbitro and arbitro.torneo_id != assigned_torneo:
                    invalid = True
                if invalid:
                    messages.error(request, 'No puedes asignar equipos o grupo de otro torneo.')
                    context = {'form': form, 'partido': partido, 'action': 'Editar'}
                    return render(request, 'admin/partidos/form.html', context)
            # Validar ubicacion (si se seleccionó) pertenece al torneo
            ubicacion = form.cleaned_data.get('ubicacion')
            if ubicacion:
                try:
                    from .models import UbicacionCampo
                    if not UbicacionCampo.objects.filter(id=ubicacion.id).filter(
                        Q(partidos__grupo__categoria__torneo_id=assigned_torneo) |
                        Q(partidos__equipo_local__categoria__torneo_id=assigned_torneo) |
                        Q(partidos__equipo_visitante__categoria__torneo_id=assigned_torneo) |
                        Q(creado_por=request.user)
                    ).exists():
                        messages.error(request, 'La ubicación seleccionada no está asociada a tu torneo.')
                        context = {'form': form, 'partido': partido, 'action': 'Editar'}
                        return render(request, 'admin/partidos/form.html', context)
                except Exception:
                    pass
            form.save()
            messages.success(request, 'Partido actualizado exitosamente.')
            return redirect('admin_partidos')
    else:
        form = PartidoForm(instance=partido, assigned_torneo=assigned_torneo, current_user=request.user)
    
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
    # Limitar por torneo si es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            grupos = grupos.filter(categoria__torneo_id=assigned_torneo)
    
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
    
    # Para el filtro de categorías (limitar si aplica)
    if assigned_torneo:
        categorias = Categoria.objects.select_related('torneo').filter(torneo_id=assigned_torneo).order_by('nombre')
    else:
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
    
    # Si el usuario es AdministradorTorneo, limitar la lista a los usuarios que él creó
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if assigned_torneo:
        from .models import UsuarioCreado
        usuarios_ids = UsuarioCreado.objects.filter(creado_por=request.user).values_list('usuario_id', flat=True)
        usuarios = User.objects.filter(id__in=usuarios_ids)
    else:
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
    
    # Agregar información de representante
    for usuario in usuarios:
        try:
            usuario.representante_info = usuario.representante
        except:
            usuario.representante_info = None
    
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
        'total_representantees': Representante.objects.filter(activo=True).count(),
    }
    return render(request, 'admin/usuarios/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_usuario(request):
    # Si el usuario es AdministradorTorneo, no puede crear usuarios con privilegios
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
    restrict_privileges = bool(assigned_torneo) and not request.user.is_superuser

    if request.method == 'POST':
        form = UsuarioForm(request.POST, restrict_privileges=restrict_privileges)
        if form.is_valid():
            # Guardar sin commitear para forzar flags si corresponde
            user = form.save(commit=False)
            # Forzar que sea usuario normal si el creador es admin de torneo
            if restrict_privileges:
                user.is_staff = False
                user.is_superuser = False
            # Manejar contraseña (UsuarioForm.save hace set_password, replicamos aquí)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            # Registrar que este usuario fue creado por el admin actual (si aplica)
            try:
                from .models import UsuarioCreado
                UsuarioCreado.objects.create(usuario=user, creado_por=request.user)
            except Exception:
                # No fallar si por alguna razón no podemos registrar la relación
                pass
            messages.success(request, f'Usuario "{user.username}" creado exitosamente.')
            return redirect('admin_usuarios')
    else:
        form = UsuarioForm(restrict_privileges=restrict_privileges)
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/usuarios/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_usuario(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    # Si el editor es AdministradorTorneo, ocultar/deshabilitar campos de privilegios en el formulario
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
    restrict_privileges = bool(assigned_torneo) and not request.user.is_superuser

    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario, restrict_privileges=restrict_privileges)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario "{user.username}" actualizado exitosamente.')
            return redirect('admin_usuarios')
    else:
        form = UsuarioEditForm(instance=usuario, restrict_privileges=restrict_privileges)
    
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

# ========== ÁRBITROS ==========

@login_required
@user_passes_test(is_admin)
def admin_arbitros(request):
    search = request.GET.get('search', '')
    torneo_id = request.GET.get('torneo')
    activo = request.GET.get('activo')

    arbitros = Arbitro.objects.select_related('usuario', 'torneo').annotate(total_partidos=Count('partidos'))
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            arbitros = arbitros.filter(torneo_id=assigned_torneo)

    if search:
        arbitros = arbitros.filter(
            Q(usuario__username__icontains=search) |
            Q(usuario__first_name__icontains=search) |
            Q(usuario__last_name__icontains=search)
        )

    if torneo_id:
        arbitros = arbitros.filter(torneo_id=torneo_id)

    if activo:
        arbitros = arbitros.filter(activo=(activo == 'true'))

    arbitros = arbitros.order_by('torneo__nombre', 'usuario__username')
    total_arbitros = arbitros.count()
    arbitros_activos = arbitros.filter(activo=True).count()

    paginator = Paginator(arbitros, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if assigned_torneo:
        torneos = Torneo.objects.filter(id=assigned_torneo)
    else:
        torneos = Torneo.objects.all().order_by('nombre')

    context = {
        'page_obj': page_obj,
        'search': search,
        'torneo_id': torneo_id,
        'activo': activo,
        'torneos': torneos,
        'total_arbitros': total_arbitros,
        'arbitros_activos': arbitros_activos,
    }
    return render(request, 'admin/arbitros/listar.html', context)


@login_required
@user_passes_test(is_admin)
def admin_crear_arbitro(request):
    assigned_torneo = None
    created_by = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            created_by = request.user

    if request.method == 'POST':
        form = ArbitroForm(request.POST, created_by=created_by, assigned_torneo=assigned_torneo)
        if form.is_valid():
            arbitro = form.save(commit=False)
            if assigned_torneo and not request.user.is_superuser:
                arbitro.torneo_id = assigned_torneo
            arbitro.save()
            messages.success(request, f'Árbitro "{arbitro.usuario.username}" asignado exitosamente.')
            return redirect('admin_arbitros')
    else:
        form = ArbitroForm(created_by=created_by, assigned_torneo=assigned_torneo)

    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/arbitros/form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_editar_arbitro(request, arbitro_id):
    arbitro = get_object_or_404(Arbitro, id=arbitro_id)
    assigned_torneo = None
    created_by = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            created_by = request.user

    if request.method == 'POST':
        form = ArbitroForm(request.POST, instance=arbitro, created_by=created_by, assigned_torneo=assigned_torneo)
        if form.is_valid():
            arbitro_obj = form.save(commit=False)
            if assigned_torneo and not request.user.is_superuser:
                arbitro_obj.torneo_id = assigned_torneo
            arbitro_obj.save()
            messages.success(request, f'Árbitro "{arbitro_obj.usuario.username}" actualizado exitosamente.')
            return redirect('admin_arbitros')
    else:
        form = ArbitroForm(instance=arbitro, created_by=created_by, assigned_torneo=assigned_torneo)

    context = {
        'form': form,
        'arbitro': arbitro,
        'action': 'Editar',
    }
    return render(request, 'admin/arbitros/form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_eliminar_arbitro(request, arbitro_id):
    arbitro = get_object_or_404(Arbitro, id=arbitro_id)
    partidos_asignados = arbitro.partidos.count()

    if request.method == 'POST':
        arbitro.delete()
        messages.success(request, f'Árbitro "{arbitro.usuario.username}" eliminado. Los partidos quedaron sin árbitro asignado.')
        return redirect('admin_arbitros')

    context = {
        'arbitro': arbitro,
        'partidos_asignados': partidos_asignados,
    }
    return render(request, 'admin/arbitros/eliminar.html', context)

# ========== CAPITANES ==========

@login_required
@user_passes_test(is_admin)
def admin_representantes(request):
    # Búsqueda y filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria')
    activo = request.GET.get('activo')
    
    representantees = Representante.objects.select_related('usuario', 'equipo', 'equipo__categoria').all()
    # Limitar por torneo si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            representantees = representantees.filter(equipo__categoria__torneo_id=assigned_torneo)
    
    if search:
        representantees = representantees.filter(
            Q(usuario__username__icontains=search) |
            Q(usuario__first_name__icontains=search) |
            Q(usuario__last_name__icontains=search) |
            Q(equipo__nombre__icontains=search)
        )
    
    if categoria_id:
        representantees = representantees.filter(equipo__categoria_id=categoria_id)
    
    if activo:
        representantees = representantees.filter(activo=(activo == 'true'))
    
    representantees = representantees.order_by('equipo__categoria__nombre', 'equipo__nombre')
    
    # Paginación
    paginator = Paginator(representantees, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Para filtros
    if assigned_torneo:
        categorias = Categoria.objects.select_related('torneo').filter(torneo_id=assigned_torneo).order_by('nombre')
    else:
        categorias = Categoria.objects.select_related('torneo').all().order_by('torneo__nombre', 'nombre')
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'categoria_id': categoria_id,
        'activo': activo,
        'categorias': categorias,
        'total_representantees': representantees.count(),
        'representantees_activos': Representante.objects.filter(activo=True).count(),
    }
    return render(request, 'admin/representantes/listar.html', context)

@login_required
@user_passes_test(is_admin)
def admin_crear_representante(request):
    # Si el usuario es AdministradorTorneo, limitar usuarios a los que él creó
    assigned_torneo = None
    created_by = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            created_by = request.user

    if request.method == 'POST':
        form = RepresentanteForm(request.POST, created_by=created_by)
        if form.is_valid():
            # Validación adicional en servidor: asegurarnos de que el usuario seleccionado fue creado por este admin
            if created_by and not request.user.is_superuser:
                try:
                    from .models import UsuarioCreado
                    usuario_sel = form.cleaned_data.get('usuario')
                    # permitir también mantener el usuario actual si existiera (no aplica en crear)
                    if not UsuarioCreado.objects.filter(usuario=usuario_sel, creado_por=request.user).exists():
                        messages.error(request, 'No puedes asignar como representante a un usuario que no hayas creado.')
                        # volver a mostrar formulario con errores
                        context = {'form': form, 'action': 'Crear'}
                        return render(request, 'admin/representantes/form.html', context)
                except Exception:
                    # Si falla la comprobación, no bloquear (pero en general no debería pasar)
                    pass
            representante = form.save()
            
            # Registrar actividad (encontrar torneos de los equipos del representante)
            equipos = representante.equipo_set.all()
            if equipos:
                torneo = equipos.first().categoria.torneo
                registrar_actividad(
                    torneo=torneo,
                    usuario=request.user,
                    tipo_accion='crear',
                    tipo_modelo='representante',
                    descripcion=f"Representante asignado: {representante.usuario.get_full_name() or representante.usuario.username}",
                    objeto_id=representante.id,
                    request=request
                )
            
            messages.success(request, f'Representante "{representante.usuario.username}" asignado exitosamente.')
            return redirect('admin_representantes')
    else:
        form = RepresentanteForm(created_by=created_by)
    
    context = {
        'form': form,
        'action': 'Crear',
    }
    return render(request, 'admin/representantes/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_representante(request, representante_id):
    representante = get_object_or_404(Representante, id=representante_id)
    # Si el editor es AdministradorTorneo, limitar usuarios a los que él creó
    assigned_torneo = None
    created_by = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            created_by = request.user

    if request.method == 'POST':
        form = RepresentanteForm(request.POST, instance=representante, created_by=created_by)
        if form.is_valid():
            # Validación adicional: si el editor es admin de torneo, no permitir asignar usuarios que no haya creado
            if created_by and not request.user.is_superuser:
                try:
                    from .models import UsuarioCreado
                    usuario_sel = form.cleaned_data.get('usuario')
                    # Permitir si el usuario fue creado por este admin o si es el usuario actual del representante
                    if usuario_sel.id != representante.usuario.id and not UsuarioCreado.objects.filter(usuario=usuario_sel, creado_por=request.user).exists():
                        messages.error(request, 'No puedes asignar como representante a un usuario que no hayas creado.')
                        context = {'form': form, 'representante': representante, 'action': 'Editar'}
                        return render(request, 'admin/representantes/form.html', context)
                except Exception:
                    pass
            representante = form.save()
            messages.success(request, f'Representante "{representante.usuario.username}" actualizado exitosamente.')
            return redirect('admin_representantes')
    else:
        form = RepresentanteForm(instance=representante, created_by=created_by)
    
    context = {
        'form': form,
        'representante': representante,
        'action': 'Editar',
    }
    return render(request, 'admin/representantes/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_eliminar_representante(request, representante_id):
    representante = get_object_or_404(Representante, id=representante_id)
    
    if request.method == 'POST':
        usuario_nombre = representante.usuario.username
        representante.delete()
        messages.success(request, f'Representante "{usuario_nombre}" removido exitosamente.')
        return redirect('admin_representantes')
    
    context = {
        'representante': representante,
    }
    return render(request, 'admin/representantes/eliminar.html', context)

# ========== ELIMINATORIAS ==========

@login_required
@user_passes_test(is_admin)
def admin_eliminatorias(request):
    # Búsqueda y filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria')
    
    eliminatorias = Eliminatoria.objects.select_related('categoria', 'categoria__torneo').all()
    # Limitar por torneo si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            eliminatorias = eliminatorias.filter(categoria__torneo_id=assigned_torneo)
    
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
    
    # Para filtros (limitar si aplica)
    if assigned_torneo:
        categorias = Categoria.objects.select_related('torneo').filter(torneo_id=assigned_torneo).order_by('nombre')
    else:
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
    # Limitar por torneo si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            partidos = partidos.filter(eliminatoria__categoria__torneo_id=assigned_torneo)
    
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
    
    # Para filtros (limitar si aplica)
    if assigned_torneo:
        eliminatorias = Eliminatoria.objects.select_related('categoria', 'categoria__torneo').filter(categoria__torneo_id=assigned_torneo).order_by('categoria__nombre', 'orden')
    else:
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
    # Limitar por torneo si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)
        if assigned_torneo:
            goleadores = goleadores.filter(Q(categoria__torneo_id=assigned_torneo) | Q(jugador__equipo__categoria__torneo_id=assigned_torneo))
    
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
    
    # Para filtros (limitar si aplica)
    if assigned_torneo:
        categorias = Categoria.objects.select_related('torneo').filter(torneo_id=assigned_torneo).order_by('nombre')
        equipos = Equipo.objects.filter(categoria__torneo_id=assigned_torneo).order_by('nombre')
    else:
        categorias = Categoria.objects.select_related('torneo').all().order_by('torneo__nombre', 'nombre')
        equipos = Equipo.objects.all().order_by('nombre')
    
    # Estadísticas (respetando el torneo asignado si aplica)
    if assigned_torneo:
        base_goleadores_qs = Goleador.objects.filter(
            Q(categoria__torneo_id=assigned_torneo) | Q(jugador__equipo__categoria__torneo_id=assigned_torneo)
        )
    else:
        base_goleadores_qs = Goleador.objects.all()

    total_goleadores = base_goleadores_qs.count()
    total_goles_anotados = base_goleadores_qs.aggregate(total=Sum('goles'))['total'] or 0
    max_goles = base_goleadores_qs.aggregate(max_goles=Max('goles'))['max_goles'] or 0
    categorias_count = base_goleadores_qs.values('categoria').distinct().count()
    
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
    # Limitar partidos si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if assigned_torneo:
        partidos = Partido.objects.filter(Q(grupo__categoria__torneo_id=assigned_torneo) | Q(grupo=None, equipo_local__categoria__torneo_id=assigned_torneo) | Q(grupo=None, equipo_visitante__categoria__torneo_id=assigned_torneo)).order_by('jornada', 'fecha')
        partidos_elim = PartidoEliminatoria.objects.filter(eliminatoria__categoria__torneo_id=assigned_torneo).order_by('eliminatoria__orden', 'fecha')
    else:
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

    # Limitar jugadores si aplica
    if assigned_torneo:
        jugadores_qs = Jugador.objects.select_related('equipo').filter(equipo__categoria__torneo_id=assigned_torneo).order_by('nombre')
    else:
        jugadores_qs = Jugador.objects.select_related('equipo').all().order_by('nombre')

    context = {
        'form': form,
        'action': 'Crear',
        'partidos': partidos,
        'partidos_elim': partidos_elim,
        'jugadores': jugadores_qs,
    }
    return render(request, 'admin/goleadores/form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_editar_goleador(request, goleador_id):
    goleador = get_object_or_404(Goleador, id=goleador_id)
    # Limitar partidos mostrados si el usuario es AdministradorTorneo
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if assigned_torneo:
        partidos = Partido.objects.filter(Q(grupo__categoria__torneo_id=assigned_torneo) | Q(grupo=None, equipo_local__categoria__torneo_id=assigned_torneo) | Q(grupo=None, equipo_visitante__categoria__torneo_id=assigned_torneo)).order_by('jornada', 'fecha')
        partidos_elim = PartidoEliminatoria.objects.filter(eliminatoria__categoria__torneo_id=assigned_torneo).order_by('eliminatoria__orden', 'fecha')
    else:
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

    # Limitar jugadores si aplica
    if assigned_torneo:
        jugadores_qs = Jugador.objects.select_related('equipo').filter(equipo__categoria__torneo_id=assigned_torneo).order_by('nombre')
    else:
        jugadores_qs = Jugador.objects.select_related('equipo').all().order_by('nombre')

    context = {
        'form': form,
        'goleador': goleador,
        'action': 'Editar',
        'partidos': partidos,
        'partidos_elim': partidos_elim,
        'jugadores': jugadores_qs,
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
    # Limitar UbicacionCampo a los campos asociados a partidos del torneo asignado
    assigned_torneo = None
    if not request.user.is_superuser:
        assigned_torneo = get_assigned_torneo_id(request.user)

    if assigned_torneo:
        campos = UbicacionCampo.objects.filter(
            Q(partidos__grupo__categoria__torneo_id=assigned_torneo) |
            Q(partidos__equipo_local__categoria__torneo_id=assigned_torneo) |
            Q(partidos__equipo_visitante__categoria__torneo_id=assigned_torneo) |
            Q(creado_por=request.user)
        ).distinct()
    else:
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
            campo = form.save(commit=False)
            campo.creado_por = request.user
            campo.save()
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


# =================== AJUSTE DE PUNTOS ===================

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AjustePuntosForm
from .models import AjustePuntos

@login_required
@user_passes_test(is_admin)
def admin_ajustar_puntos(request):
    """Lista de ajustes de puntos realizados"""
    assigned_torneo_id = get_assigned_torneo_id(request.user)
    
    # Filtrar ajustes según el torneo asignado
    if assigned_torneo_id:
        ajustes = AjustePuntos.objects.filter(
            categoria__torneo_id=assigned_torneo_id
        ).select_related('equipo', 'categoria', 'realizado_por').order_by('-fecha_creacion')
    else:
        ajustes = AjustePuntos.objects.select_related('equipo', 'categoria', 'realizado_por').order_by('-fecha_creacion')
    
    context = {
        'ajustes': ajustes,
        'total_ajustes': ajustes.count(),
    }
    return render(request, 'admin/torneos/ajustar_puntos.html', context)


@login_required
@user_passes_test(is_admin)
def admin_crear_ajuste_puntos(request):
    """Crear nuevo ajuste de puntos"""
    assigned_torneo_id = get_assigned_torneo_id(request.user)
    
    if request.method == 'POST':
        form = AjustePuntosForm(request.POST)
        if form.is_valid():
            ajuste = form.save(commit=False)
            ajuste.realizado_por = request.user
            ajuste.save()
            messages.success(
                request, 
                f'Ajuste de puntos realizado: {ajuste.equipo.nombre} {ajuste.puntos_ajuste:+d} puntos'
            )
            return redirect('admin_ajustar_puntos')
    else:
        form = AjustePuntosForm()
        # Limitar categorías si es administrador de un torneo específico
        if assigned_torneo_id:
            form.fields['categoria'].queryset = Categoria.objects.filter(torneo_id=assigned_torneo_id)
            form.fields['equipo'].queryset = Equipo.objects.filter(categoria__torneo_id=assigned_torneo_id)
    
    context = {
        'form': form,
        'titulo': 'Crear Ajuste de Puntos',
    }
    return render(request, 'admin/torneos/crear_ajuste_puntos.html', context)


@login_required
@user_passes_test(is_admin)
def admin_editar_ajuste_puntos(request, ajuste_id):
    """Editar un ajuste de puntos"""
    ajuste = get_object_or_404(AjustePuntos, id=ajuste_id)
    assigned_torneo_id = get_assigned_torneo_id(request.user)
    
    # Verificar permisos
    if assigned_torneo_id and ajuste.categoria.torneo_id != assigned_torneo_id:
        messages.error(request, 'No tienes permiso para editar este ajuste.')
        return redirect('admin_ajustar_puntos')
    
    if request.method == 'POST':
        form = AjustePuntosForm(request.POST, instance=ajuste)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ajuste de puntos actualizado exitosamente.')
            return redirect('admin_ajustar_puntos')
    else:
        form = AjustePuntosForm(instance=ajuste)
        if assigned_torneo_id:
            form.fields['categoria'].queryset = Categoria.objects.filter(torneo_id=assigned_torneo_id)
            form.fields['equipo'].queryset = Equipo.objects.filter(categoria__torneo_id=assigned_torneo_id)
    
    context = {
        'form': form,
        'ajuste': ajuste,
        'titulo': 'Editar Ajuste de Puntos',
    }
    return render(request, 'admin/torneos/crear_ajuste_puntos.html', context)


@login_required
@user_passes_test(is_admin)
@require_POST
def admin_eliminar_ajuste_puntos(request, ajuste_id):
    """Eliminar un ajuste de puntos"""
    ajuste = get_object_or_404(AjustePuntos, id=ajuste_id)
    assigned_torneo_id = get_assigned_torneo_id(request.user)
    
    # Verificar permisos
    if assigned_torneo_id and ajuste.categoria.torneo_id != assigned_torneo_id:
        messages.error(request, 'No tienes permiso para eliminar este ajuste.')
        return redirect('admin_ajustar_puntos')
    
    equipo_nombre = ajuste.equipo.nombre
    puntos_str = f"{ajuste.puntos_ajuste:+d}"
    ajuste.delete()
    messages.success(request, f'Ajuste de puntos eliminado: {equipo_nombre} {puntos_str}')
    return redirect('admin_ajustar_puntos')


# =================== REGISTROS DE ACTIVIDAD ===================
@login_required
@user_passes_test(is_admin)
def admin_actividades(request):
    from .models import RegistroActividad
    
    # Obtener torneo asignado
    assigned_torneo_id = None
    if not request.user.is_superuser:
        assigned_torneo_id = get_assigned_torneo_id(request.user)
    
    # Filtrar actividades por torneo asignado
    actividades = RegistroActividad.objects.select_related('torneo', 'usuario')
    if assigned_torneo_id:
        actividades = actividades.filter(torneo_id=assigned_torneo_id)
    
    # Filtros adicionales
    torneo_filtro = request.GET.get('torneo')
    usuario_filtro = request.GET.get('usuario')
    tipo_accion_filtro = request.GET.get('tipo_accion')
    tipo_modelo_filtro = request.GET.get('tipo_modelo')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if torneo_filtro:
        actividades = actividades.filter(torneo_id=torneo_filtro)
    if usuario_filtro:
        actividades = actividades.filter(usuario_id=usuario_filtro)
    if tipo_accion_filtro:
        actividades = actividades.filter(tipo_accion=tipo_accion_filtro)
    if tipo_modelo_filtro:
        actividades = actividades.filter(tipo_modelo=tipo_modelo_filtro)
    if fecha_desde:
        from datetime import datetime
        actividades = actividades.filter(fecha_hora__gte=datetime.strptime(fecha_desde, '%Y-%m-%d'))
    if fecha_hasta:
        from datetime import datetime
        actividades = actividades.filter(fecha_hora__lte=datetime.strptime(fecha_hasta, '%Y-%m-%d'))
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(actividades, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener opciones para filtros
    if assigned_torneo_id:
        torneos_disponibles = Torneo.objects.filter(id=assigned_torneo_id)
    else:
        torneos_disponibles = Torneo.objects.all()
    
    usuarios_con_actividad = User.objects.filter(
        id__in=RegistroActividad.objects.values_list('usuario_id', flat=True).distinct()
    ).order_by('username')
    
    context = {
        'page_obj': page_obj,
        'torneos_disponibles': torneos_disponibles,
        'usuarios_con_actividad': usuarios_con_actividad,
        'tipo_accion_choices': RegistroActividad.TIPO_ACCION_CHOICES,
        'tipo_modelo_choices': RegistroActividad.TIPO_MODELO_CHOICES,
        'torneo_filtro': torneo_filtro,
        'usuario_filtro': usuario_filtro,
        'tipo_accion_filtro': tipo_accion_filtro,
        'tipo_modelo_filtro': tipo_modelo_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'admin/actividades/listar.html', context)
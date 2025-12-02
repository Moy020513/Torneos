from django.contrib import admin
from django.db import models
from .models import Eliminatoria, Torneo, Categoria, Equipo, Jugador, Capitan, Partido, PartidoEliminatoria, Goleador, ParticipacionJugador
from .models import AdministradorTorneo
from .forms import EquipoAdminForm
from django.utils.html import format_html

@admin.register(Eliminatoria)
class EliminatoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'orden')
    list_filter = ('categoria', 'nombre')
    search_fields = ('nombre',)

# Branding del sitio de administración
admin.site.site_header = "Panel de Torneos"
admin.site.site_title = "Admin Torneos"
admin.site.index_title = "Administración General"

@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'formato_torneo', 'activo', 'logo', 'reglamento_link')
    list_filter = ('activo', 'formato_torneo')
    search_fields = ('nombre', 'descripcion')
    actions = ['delete_images', 'cleanup_orphaned_images']

    def delete_images(self, request, queryset):
        from django.contrib import messages
        import os
        from .models import Equipo, Jugador
        total_deleted = 0
        for torneo in queryset:
            # Eliminar logo del torneo
            if torneo.logo and os.path.exists(torneo.logo.path):
                os.remove(torneo.logo.path)
                torneo.logo = None
                torneo.color1 = None
                torneo.color2 = None
                torneo.color3 = None
                torneo.save(update_fields=['logo', 'color1', 'color2', 'color3'])
                total_deleted += 1

            # Eliminar logos de equipos
            equipos = Equipo.objects.filter(categoria__torneo=torneo)
            for equipo in equipos:
                if equipo.logo and os.path.exists(equipo.logo.path):
                    os.remove(equipo.logo.path)
                    equipo.logo = None
                    equipo.save(update_fields=['logo'])
                    total_deleted += 1

            # Eliminar fotos de jugadores
            jugadores = Jugador.objects.filter(equipo__categoria__torneo=torneo)
            for jugador in jugadores:
                if jugador.foto and os.path.exists(jugador.foto.path):
                    os.remove(jugador.foto.path)
                    jugador.foto = None
                    jugador.save(update_fields=['foto'])
                    total_deleted += 1

        messages.success(request, f'Se eliminaron {total_deleted} imágenes de {queryset.count()} torneos.')
    
    delete_images.short_description = "Eliminar todas las imágenes de los torneos seleccionados"

    def cleanup_orphaned_images(self, request, queryset):
        from django.contrib import messages
        import os
        from django.conf import settings
        from .models import Torneo, Equipo, Jugador
        media_root = settings.MEDIA_ROOT
        total_deleted = 0

        # Obtener paths de imágenes en DB
        torneo_paths = set(Torneo.objects.exclude(logo='').values_list('logo', flat=True))
        equipo_paths = set(Equipo.objects.exclude(logo='').values_list('logo', flat=True))
        jugador_paths = set(Jugador.objects.exclude(foto='').values_list('foto', flat=True))

        all_db_paths = torneo_paths | equipo_paths | jugador_paths

        # Directorios a escanear
        dirs_to_check = ['torneos/logos', 'equipos/logos', 'jugadores/fotos']

        for dir_path in dirs_to_check:
            full_dir = os.path.join(media_root, dir_path)
            if os.path.exists(full_dir):
                for file in os.listdir(full_dir):
                    file_path = os.path.join(dir_path, file)
                    if file_path not in all_db_paths:
                        full_file_path = os.path.join(media_root, file_path)
                        if os.path.isfile(full_file_path):
                            os.remove(full_file_path)
                            total_deleted += 1

        messages.success(request, f'Se eliminaron {total_deleted} imágenes huérfanas.')
    
    cleanup_orphaned_images.short_description = "Limpiar imágenes huérfanas no asociadas"

    def reglamento_link(self, obj):
        if obj.reglamento:
            return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Descargar</a>', obj.reglamento.url)
        return '-'
    reglamento_link.short_description = 'Reglamento'

@admin.register(Categoria)

class CategoriaAdmin(admin.ModelAdmin):
    def equipos_descansan_por_jornada(self, categoria):
        from .models import Partido, Equipo
        equipos = list(Equipo.objects.filter(categoria=categoria))
        n = len(equipos)
        if n % 2 == 0:
            return "No hay descansos (número par de equipos)"
        total_jornadas = n
        partidos = list(Partido.objects.filter(grupo__categoria=categoria).order_by('jornada', 'id'))
        equipos_existentes = equipos.copy()
        descansos = []
        for jornada in range(1, total_jornadas + 1):
            equipos_en_jornada = set()
            partidos_jornada = [p for p in partidos if p.jornada == jornada]
            for p in partidos_jornada:
                equipos_en_jornada.add(p.equipo_local)
                equipos_en_jornada.add(p.equipo_visitante)
            equipo_descanso = None
            for eq in equipos_existentes:
                if eq not in equipos_en_jornada:
                    equipo_descanso = eq
                    break
            descansos.append((jornada, equipo_descanso.nombre if equipo_descanso else "N/A"))
        return descansos

    actions = ['generar_calendario_ida', 'generar_calendario_ida_vuelta', 'integrar_nuevo_equipo']
    def integrar_nuevo_equipo(self, request, queryset):
        from django.contrib import messages
        from .models import Equipo, Grupo, Partido
        from datetime import datetime
        for categoria in queryset:
            equipos = list(Equipo.objects.filter(categoria=categoria))
            total_equipos = len(equipos)
            if total_equipos < 2:
                messages.warning(request, f"La categoría '{categoria.nombre}' necesita al menos 2 equipos.")
                continue
            # Detectar jornadas ya jugadas
            partidos_jugados = Partido.objects.filter(grupo__categoria=categoria, jugado=True).count()
            grupo, created = Grupo.objects.get_or_create(
                categoria=categoria,
                nombre="Grupo Único",
                defaults={'descripcion': 'Grupo principal de la categoría'}
            )
            if partidos_jugados == 0:
                n = total_equipos
                equipos_existentes = equipos[:-1]  # Todos menos el nuevo
                nuevo_equipo = equipos[-1]
                partidos = list(Partido.objects.filter(grupo__categoria=categoria).order_by('jornada', 'id'))
                if (n - 1) % 2 == 0 and n % 2 == 1:
                    # Pasó de par a impar: integrar nuevo equipo con mínimo alteración
                    total_jornadas = n
                    # Jornada 1: nuevo equipo descansa
                    Partido.objects.create(
                        grupo=grupo,
                        jornada=1,
                        equipo_local=nuevo_equipo,
                        equipo_visitante=nuevo_equipo,
                        ubicacion=None,
                        fecha=None
                    )
                    # Jornadas siguientes: modificar un partido por jornada
                    for jornada in range(2, total_jornadas + 1):
                        partidos_jornada = [p for p in partidos if p.jornada == jornada]
                        if not partidos_jornada:
                            continue
                        # Elegir el primer partido de la jornada para modificar
                        partido_a_modificar = partidos_jornada[0]
                        equipo_descansa = partido_a_modificar.equipo_local
                        # El nuevo equipo toma el lugar de equipo_local
                        partido_a_modificar.equipo_local = nuevo_equipo
                        partido_a_modificar.campo = 'Por definir'
                        partido_a_modificar.fecha = None
                        partido_a_modificar.save()
                        # Registrar el descanso
                        Partido.objects.create(
                            grupo=partido_a_modificar.grupo,
                            jornada=jornada,
                            equipo_local=equipo_descansa,
                            equipo_visitante=equipo_descansa,
                            ubicacion=None,
                            fecha=None
                        )
                    messages.success(request, f"El nuevo equipo '{nuevo_equipo.nombre}' fue integrado correctamente. Descansa en la J1 y en cada jornada un equipo original descansa y el nuevo juega en su lugar.")
                else:
                    # Lógica anterior para impar a par o generación normal
                    total_jornadas = n - 1
                    partidos_por_jornada_antes = (n - 1) // 2
                    partidos_por_jornada_despues = n // 2
                    equipos_descansaban = []
                    for jornada in range(1, total_jornadas + 1):
                        equipos_en_jornada = set()
                        partidos_jornada = [p for p in partidos if p.jornada == jornada]
                        for p in partidos_jornada:
                            equipos_en_jornada.add(p.equipo_local)
                            equipos_en_jornada.add(p.equipo_visitante)
                        equipo_descanso = None
                        for eq in equipos_existentes:
                            if eq not in equipos_en_jornada:
                                equipo_descanso = eq
                                break
                        equipos_descansaban.append(equipo_descanso)
                    for jornada, equipo_descanso in enumerate(equipos_descansaban, start=1):
                        if equipo_descanso is not None:
                            Partido.objects.create(
                                grupo=partidos[0].grupo if partidos else None,
                                jornada=jornada,
                                equipo_local=equipo_descanso,
                                equipo_visitante=nuevo_equipo,
                                ubicacion=None,
                                fecha=None
                            )
                    messages.success(request, f"El nuevo equipo '{nuevo_equipo.nombre}' fue integrado correctamente enfrentando al equipo que descansaba en cada jornada. El número de partidos por jornada aumentó.")
            else:
                # Hay partidos jugados, integrar solo en jornadas futuras
                jornadas_jugadas = set(Partido.objects.filter(grupo__categoria=categoria, jugado=True).values_list('jornada', flat=True))
                max_jornada = Partido.objects.filter(grupo__categoria=categoria).aggregate(maxj=models.Max('jornada'))['maxj'] or 0
                nuevo_equipo = equipos[-1]  # Asume que el último equipo agregado es el nuevo
                # Para cada jornada ya jugada, el nuevo equipo descansa
                for jornada in jornadas_jugadas:
                    Partido.objects.create(
                        grupo=grupo,
                        jornada=jornada,
                        equipo_local=nuevo_equipo,
                        equipo_visitante=None,
                        ubicacion=None,
                        fecha=None
                    )
                # Para jornadas futuras, recalcular round-robin con todos los equipos
                n = total_equipos
                if n % 2 == 1:
                    equipos_rr = equipos.copy()
                else:
                    equipos_rr = equipos.copy()
                    equipos_rr.append(None)  # Para round-robin impar
                    n += 1
                partidos_por_jornada = n // 2
                total_jornadas = n - 1
                for jornada in range(max_jornada + 1, total_jornadas + 1):
                    for i in range(partidos_por_jornada):
                        local = equipos_rr[i]
                        visitante = equipos_rr[n - 1 - i]
                        if local is not None and visitante is not None:
                            Partido.objects.create(
                                grupo=grupo,
                                jornada=jornada,
                                equipo_local=local,
                                equipo_visitante=visitante,
                                ubicacion=None,
                                fecha=None
                            )
                    equipos_rr.insert(1, equipos_rr.pop())
                messages.success(request, f"El nuevo equipo '{nuevo_equipo.nombre}' fue integrado al calendario de '{categoria.nombre}'.")
    integrar_nuevo_equipo.short_description = "Integrar nuevo equipo al calendario (respetando jornadas jugadas y descansos)"
    def mostrar_descansos(self, obj):
        descansos = self.equipos_descansan_por_jornada(obj)
        if isinstance(descansos, str):
            return descansos
        return ", ".join([f"J{j}: {e}" for j, e in descansos])
    mostrar_descansos.short_description = "Descansos por jornada (impar)"

    list_display = ('nombre', 'torneo', 'max_equipos', 'tiene_eliminatorias', 'mostrar_descansos')
    list_filter = ('torneo', 'tiene_eliminatorias')
    search_fields = ('nombre', 'descripcion')

    actions = ['generar_calendario_ida', 'generar_calendario_ida_vuelta', 'integrar_nuevo_equipo']


    def generar_calendario_ida(self, request, queryset):
        """Genera calendario solo ida (round robin simple)"""
        from django.contrib import messages
        from datetime import datetime
        from .models import Equipo, Grupo, Partido
        total = 0
        for categoria in queryset:
            equipos = list(Equipo.objects.filter(categoria=categoria))
            if len(equipos) < 2:
                messages.warning(request, f"La categoría '{categoria.nombre}' necesita al menos 2 equipos.")
                continue
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
            for jornada in range(1, total_jornadas + 1):
                for i in range(partidos_por_jornada):
                    # Alternar local/visitante por jornada para equidad
                    if jornada % 2 == 1:
                        local = equipos_rr[i]
                        visitante = equipos_rr[n - 1 - i]
                    else:
                        local = equipos_rr[n - 1 - i]
                        visitante = equipos_rr[i]
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
            messages.success(request, f"Calendario (solo ida) generado para '{categoria.nombre}' ({total_jornadas} jornadas, {total} partidos).")
    generar_calendario_ida.short_description = "Generar calendario solo ida (round robin simple)"

    def generar_calendario_ida_vuelta(self, request, queryset):
        """Genera calendario ida y vuelta (round robin doble)"""
        from django.contrib import messages
        from datetime import datetime
        from .models import Equipo, Grupo, Partido
        total = 0
        for categoria in queryset:
            equipos = list(Equipo.objects.filter(categoria=categoria))
            if len(equipos) < 2:
                messages.warning(request, f"La categoría '{categoria.nombre}' necesita al menos 2 equipos.")
                continue
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
            # Ida
            temp_equipos = equipos_rr.copy()
            for jornada in range(1, total_jornadas + 1):
                for i in range(partidos_por_jornada):
                    local = temp_equipos[i]
                    visitante = temp_equipos[n - 1 - i]
                    if local is not None and visitante is not None:
                        Partido.objects.create(
                            grupo=grupo,
                            jornada=jornada,
                            equipo_local=local,
                            equipo_visitante=visitante,
                            ubicacion=None
                        )
                        total += 1
                temp_equipos = [temp_equipos[0]] + [temp_equipos[-1]] + temp_equipos[1:-1]
            # Vuelta (local/visitante invertidos, misma rotación)
            temp_equipos = equipos_rr.copy()
            for jornada in range(1, total_jornadas + 1):
                for i in range(partidos_por_jornada):
                    local = temp_equipos[i]
                    visitante = temp_equipos[n - 1 - i]
                    if local is not None and visitante is not None:
                        Partido.objects.create(
                            grupo=grupo,
                            jornada=total_jornadas + jornada,
                            equipo_local=visitante,
                            equipo_visitante=local,
                            ubicacion=None
                        )
                        total += 1
                temp_equipos = [temp_equipos[0]] + [temp_equipos[-1]] + temp_equipos[1:-1]
            messages.success(request, f"Calendario (ida y vuelta) generado para '{categoria.nombre}' ({total_jornadas*2} jornadas, {total} partidos).")
    generar_calendario_ida_vuelta.short_description = "Generar calendario ida y vuelta (round robin doble)"

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    form = EquipoAdminForm
    list_display = ('nombre', 'categoria', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre',)

    class Media:
        js = ('admin/js/filtrar_categorias.js',)

@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'equipo', 'numero_camiseta', 'posicion', 'activo', 'verificado', 'verificado_por', 'fecha_verificacion')
    list_filter = ('equipo', 'posicion', 'activo', 'verificado')
    search_fields = ('nombre', 'apellido')
    actions = ['marcar_como_verificado', 'desmarcar_como_verificado']

    @admin.action(description="Marcar seleccionados como verificados")
    def marcar_como_verificado(self, request, queryset):
        from django.utils import timezone
        from django.contrib import messages
        updated = 0
        for jugador in queryset:
            jugador.verificado = True
            jugador.verificado_por = request.user
            jugador.fecha_verificacion = timezone.now()
            jugador.save(update_fields=['verificado', 'verificado_por', 'fecha_verificacion'])
            updated += 1
        messages.success(request, f"{updated} jugador(es) marcados como verificados.")

    @admin.action(description="Desmarcar verificados")
    def desmarcar_como_verificado(self, request, queryset):
        from django.contrib import messages
        updated = 0
        for jugador in queryset:
            jugador.verificado = False
            jugador.verificado_por = None
            jugador.fecha_verificacion = None
            jugador.save(update_fields=['verificado', 'verificado_por', 'fecha_verificacion'])
            updated += 1
        messages.success(request, f"{updated} jugador(es) desmarcados como verificados.")

@admin.register(Capitan)
class CapitanAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'equipo', 'activo')
    list_filter = ('activo',)
    search_fields = ('usuario__username', 'equipo__nombre')

@admin.register(Partido)

class PartidoAdmin(admin.ModelAdmin):
    def mostrar_descansos(self, obj):
        from .models import Partido, Equipo, Categoria
        if not obj.grupo or not obj.grupo.categoria:
            return "-"
        categoria = obj.grupo.categoria
        equipos = list(Equipo.objects.filter(categoria=categoria))
        n = len(equipos)
        if n % 2 == 0:
            return "No hay descansos (par)"
        total_jornadas = n
        partidos = list(Partido.objects.filter(grupo__categoria=categoria).order_by('jornada', 'id'))
        equipos_existentes = equipos.copy()
        descansos = []
        for jornada in range(1, total_jornadas + 1):
            equipos_en_jornada = set()
            partidos_jornada = [p for p in partidos if p.jornada == jornada]
            for p in partidos_jornada:
                equipos_en_jornada.add(p.equipo_local)
                equipos_en_jornada.add(p.equipo_visitante)
            equipo_descanso = None
            for eq in equipos_existentes:
                if eq not in equipos_en_jornada:
                    equipo_descanso = eq
                    break
            descansos.append(f"J{jornada}: {equipo_descanso.nombre if equipo_descanso else 'N/A'}")
        return ", ".join(descansos)

    mostrar_descansos.short_description = "Descansos por jornada (impar)"

    list_display = ('equipo_local', 'equipo_visitante', 'jornada', 'goles_local', 'goles_visitante', 'jugado')
    list_filter = ('grupo', 'jornada', 'jugado')
    search_fields = ('equipo_local__nombre', 'equipo_visitante__nombre')

    actions = ['generar_calendario_desde_partido', 'eliminar_calendario']

    def save_model(self, request, obj, form, change):
        # Marcar automáticamente como jugado si se cargan goles (no cubre 0-0)
        try:
            goles_local = form.cleaned_data.get('goles_local', obj.goles_local)
            goles_visitante = form.cleaned_data.get('goles_visitante', obj.goles_visitante)
        except Exception:
            goles_local = obj.goles_local
            goles_visitante = obj.goles_visitante
        if (goles_local or 0) > 0 or (goles_visitante or 0) > 0:
            obj.jugado = True
        super().save_model(request, obj, form, change)

    @admin.action(description="Marcar seleccionados como jugados")
    def marcar_como_jugados(self, request, queryset):
        updated = queryset.update(jugado=True)
        from django.contrib import messages
        messages.success(request, f"{updated} partido(s) marcados como jugados.")
    actions += ['marcar_como_jugados']

    def eliminar_calendario(self, request, queryset):
        from django.contrib import messages
        from .models import Partido
        categorias = set()
        for partido in queryset:
            if partido.grupo and partido.grupo.categoria:
                categorias.add(partido.grupo.categoria)
        if not categorias:
            messages.warning(request, "No se encontraron categorías asociadas a los partidos seleccionados.")
            return
        total = 0
        for categoria in categorias:
            deleted, _ = Partido.objects.filter(grupo__categoria=categoria).delete()
            total += deleted
            messages.success(request, f"Se eliminaron {deleted} partidos del calendario de la categoría '{categoria.nombre}'.")
    eliminar_calendario.short_description = "Eliminar todo el calendario de la categoría seleccionada"

    def generar_calendario_desde_partido(self, request, queryset):
        from django.contrib import messages
        from datetime import datetime
        from .models import Categoria, Equipo, Grupo, Partido
        categorias = set()
        for partido in queryset:
            if partido.grupo and partido.grupo.categoria:
                categorias.add(partido.grupo.categoria)
        if not categorias:
            messages.warning(request, "No se encontraron categorías asociadas a los partidos seleccionados.")
            return
        total = 0
        for categoria in categorias:
            equipos = list(Equipo.objects.filter(categoria=categoria))
            if len(equipos) < 2:
                messages.warning(request, f"La categoría '{categoria.nombre}' necesita al menos 2 equipos.")
                continue
            n = len(equipos)
            if n % 2 == 1:
                equipos.append(None)
                n += 1
            partidos_por_jornada = n // 2
            total_jornadas = n - 1
            grupo, created = Grupo.objects.get_or_create(
                categoria=categoria,
                nombre="Grupo Único",
                defaults={'descripcion': 'Grupo principal de la categoría'}
            )
            Partido.objects.filter(grupo__categoria=categoria).delete()
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
                            fecha=datetime.now()
                        )
                        total += 1
                equipos.insert(1, equipos.pop())
            messages.success(request, f"Calendario generado para '{categoria.nombre}' ({total_jornadas} jornadas, {total} partidos).")
    generar_calendario_desde_partido.short_description = "Generar calendario de partidos para la categoría de los partidos seleccionados"

@admin.register(PartidoEliminatoria)
class PartidoEliminatoriaAdmin(admin.ModelAdmin):
    list_display = ('equipo_local', 'equipo_visitante', 'eliminatoria', 'goles_local', 'goles_visitante', 'jugado')
    list_filter = ('eliminatoria', 'jugado')
    search_fields = ('equipo_local__nombre', 'equipo_visitante__nombre')

    def save_model(self, request, obj, form, change):
        # Marcar automáticamente como jugado si se cargan goles (no cubre 0-0)
        try:
            goles_local = form.cleaned_data.get('goles_local', obj.goles_local)
            goles_visitante = form.cleaned_data.get('goles_visitante', obj.goles_visitante)
        except Exception:
            goles_local = obj.goles_local
            goles_visitante = obj.goles_visitante
        if (goles_local or 0) > 0 or (goles_visitante or 0) > 0:
            obj.jugado = True
        super().save_model(request, obj, form, change)

    @admin.action(description="Marcar seleccionados como jugados")
    def marcar_como_jugados(self, request, queryset):
        updated = queryset.update(jugado=True)
        from django.contrib import messages
        messages.success(request, f"{updated} partido(s) de eliminatoria marcados como jugados.")
    actions = ['marcar_como_jugados']

@admin.register(Goleador)
class GoleadorAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'partido', 'partido_eliminatoria', 'goles')
    list_filter = ('partido', 'partido_eliminatoria')
    search_fields = ('jugador__nombre', 'jugador__apellido')

@admin.register(ParticipacionJugador)
class ParticipacionJugadorAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'partido', 'titular', 'minutos_jugados', 'observaciones', 'fecha_creacion')
    list_filter = ('titular', 'jugador', 'partido')
    search_fields = ('jugador__nombre', 'jugador__apellido', 'partido__equipo_local__nombre', 'partido__equipo_visitante__nombre')

# Reubicar ParticipacionJugador en la sección adecuada del admin
class GestionParticipacionesAdminArea(admin.AdminSite):
    site_header = 'Gestión de Participaciones'
    site_title = 'Participaciones'
    index_title = 'Participaciones de Jugadores'

# Si quieres que aparezca en una sección personalizada, puedes crear un AppConfig o agruparlo en el admin usando etiquetas.
# Pero por defecto, ParticipacionJugador ya aparece en el menú principal del admin.

# Si quieres que aparezca bajo "Gestión de Partidos" o con un nombre personalizado:
ParticipacionJugadorAdmin.verbose_name_plural = "Partidos Jugados por Jugador"


# Registro del nuevo modelo AdministradorTorneo para que el superusuario pueda
# asignar usuarios responsables de cada torneo desde el admin estándar.
@admin.register(AdministradorTorneo)
class AdministradorTorneoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'torneo', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'torneo')
    search_fields = ('usuario__username', 'torneo__nombre')
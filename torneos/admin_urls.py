from django.urls import path
from . import admin_views
from django.urls import path

# URLs del Panel de Administración Personalizado
admin_urlpatterns = [
    path('panel/torneos/eliminar-imagenes-huerfanas/', admin_views.admin_eliminar_imagenes_huerfanas, name='admin_eliminar_imagenes_huerfanas'),
    # Dashboard
    path('panel/', admin_views.admin_dashboard, name='admin_dashboard'),
    # Participaciones de Jugadores
    path('panel/participaciones/', admin_views.admin_participaciones, name='admin_participaciones'),
    path('panel/participaciones/crear/', admin_views.admin_crear_participacion, name='admin_crear_participacion'),
    path('panel/participaciones/crear-multiples/', admin_views.admin_crear_participaciones_multiples, name='admin_crear_participaciones_multiples'),
    path('panel/participaciones/<int:participacion_id>/editar/', admin_views.admin_editar_participacion, name='admin_editar_participacion'),
    path('panel/participaciones/<int:participacion_id>/eliminar/', admin_views.admin_eliminar_participacion, name='admin_eliminar_participacion'),

    # Torneos
    path('panel/torneos/', admin_views.admin_torneos, name='admin_torneos'),
    path('panel/torneos/crear/', admin_views.admin_crear_torneo, name='admin_crear_torneo'),
    path('panel/torneos/<int:torneo_id>/editar/', admin_views.admin_editar_torneo, name='admin_editar_torneo'),
    path('panel/torneos/<int:torneo_id>/eliminar/', admin_views.admin_eliminar_torneo, name='admin_eliminar_torneo'),
    path('panel/torneos/portadas/<int:portada_id>/eliminar/', admin_views.admin_eliminar_portada, name='admin_eliminar_portada'),

    # Categorías
    path('panel/categorias/', admin_views.admin_categorias, name='admin_categorias'),
    path('panel/categorias/crear/', admin_views.admin_crear_categoria, name='admin_crear_categoria'),
    path('panel/categorias/<int:categoria_id>/editar/', admin_views.admin_editar_categoria, name='admin_editar_categoria'),
    path('panel/categorias/<int:categoria_id>/eliminar/', admin_views.admin_eliminar_categoria, name='admin_eliminar_categoria'),
    path('panel/categorias/<int:categoria_id>/generar-calendario/', admin_views.admin_generar_calendario, name='admin_generar_calendario'),
    path('panel/categorias/<int:categoria_id>/integrar-equipo/', admin_views.admin_integrar_equipo_calendario, name='admin_integrar_equipo_calendario'),

    # Equipos
    path('panel/equipos/', admin_views.admin_equipos, name='admin_equipos'),
    path('panel/equipos/crear/', admin_views.admin_crear_equipo, name='admin_crear_equipo'),
    path('panel/equipos/<int:equipo_id>/editar/', admin_views.admin_editar_equipo, name='admin_editar_equipo'),
    path('panel/equipos/<int:equipo_id>/eliminar/', admin_views.admin_eliminar_equipo, name='admin_eliminar_equipo'),

    # Jugadores
    path('panel/jugadores/', admin_views.admin_jugadores, name='admin_jugadores'),
    path('panel/jugadores/crear/', admin_views.admin_crear_jugador, name='admin_crear_jugador'),
    path('panel/jugadores/<int:jugador_id>/editar/', admin_views.admin_editar_jugador, name='admin_editar_jugador'),
    path('panel/jugadores/<int:jugador_id>/eliminar/', admin_views.admin_eliminar_jugador, name='admin_eliminar_jugador'),
        path('panel/jugadores/<int:jugador_id>/detalle/', admin_views.admin_detalle_jugador, name='admin_detalle_jugador'),

    # Partidos
    path('panel/partidos/', admin_views.admin_partidos, name='admin_partidos'),
    path('panel/partidos/crear/', admin_views.admin_crear_partido, name='admin_crear_partido'),
    path('panel/partidos/<int:partido_id>/editar/', admin_views.admin_editar_partido, name='admin_editar_partido'),
    path('panel/partidos/<int:partido_id>/eliminar/', admin_views.admin_eliminar_partido, name='admin_eliminar_partido'),

    # Ajuste de Puntos
    path('panel/ajustar-puntos/', admin_views.admin_ajustar_puntos, name='admin_ajustar_puntos'),
    path('panel/ajustar-puntos/crear/', admin_views.admin_crear_ajuste_puntos, name='admin_crear_ajuste_puntos'),
    path('panel/ajustar-puntos/<int:ajuste_id>/editar/', admin_views.admin_editar_ajuste_puntos, name='admin_editar_ajuste_puntos'),
    path('panel/ajustar-puntos/<int:ajuste_id>/eliminar/', admin_views.admin_eliminar_ajuste_puntos, name='admin_eliminar_ajuste_puntos'),

    # Grupos
    path('panel/grupos/', admin_views.admin_grupos, name='admin_grupos'),
    path('panel/grupos/crear/', admin_views.admin_crear_grupo, name='admin_crear_grupo'),
    path('panel/grupos/<int:grupo_id>/editar/', admin_views.admin_editar_grupo, name='admin_editar_grupo'),
    path('panel/grupos/<int:grupo_id>/eliminar/', admin_views.admin_eliminar_grupo, name='admin_eliminar_grupo'),

    # Usuarios
    path('panel/usuarios/', admin_views.admin_usuarios, name='admin_usuarios'),
    path('panel/usuarios/crear/', admin_views.admin_crear_usuario, name='admin_crear_usuario'),
    path('panel/usuarios/<int:usuario_id>/editar/', admin_views.admin_editar_usuario, name='admin_editar_usuario'),
    path('panel/usuarios/<int:usuario_id>/eliminar/', admin_views.admin_eliminar_usuario, name='admin_eliminar_usuario'),

    # Árbitros
    path('panel/arbitros/', admin_views.admin_arbitros, name='admin_arbitros'),
    path('panel/arbitros/crear/', admin_views.admin_crear_arbitro, name='admin_crear_arbitro'),
    path('panel/arbitros/<int:arbitro_id>/editar/', admin_views.admin_editar_arbitro, name='admin_editar_arbitro'),
    path('panel/arbitros/<int:arbitro_id>/eliminar/', admin_views.admin_eliminar_arbitro, name='admin_eliminar_arbitro'),

    # Capitanes
    path('panel/representantes/', admin_views.admin_representantes, name='admin_representantes'),
    path('panel/representantes/crear/', admin_views.admin_crear_representante, name='admin_crear_representante'),
    path('panel/representantes/<int:representante_id>/editar/', admin_views.admin_editar_representante, name='admin_editar_representante'),
    path('panel/representantes/<int:representante_id>/eliminar/', admin_views.admin_eliminar_representante, name='admin_eliminar_representante'),

    # Eliminatorias
    path('eliminatorias/', admin_views.admin_eliminatorias, name='admin_eliminatorias'),
    path('eliminatorias/crear/', admin_views.admin_crear_eliminatoria, name='admin_crear_eliminatoria'),
    path('eliminatorias/editar/<int:eliminatoria_id>/', admin_views.admin_editar_eliminatoria, name='admin_editar_eliminatoria'),
    path('eliminatorias/eliminar/<int:eliminatoria_id>/', admin_views.admin_eliminar_eliminatoria, name='admin_eliminar_eliminatoria'),

    # Partidos Eliminatoria
    path('partidos-eliminatoria/', admin_views.admin_partidos_eliminatoria, name='admin_partidos_eliminatoria'),
    path('partidos-eliminatoria/crear/', admin_views.admin_crear_partido_eliminatoria, name='admin_crear_partido_eliminatoria'),
    path('partidos-eliminatoria/editar/<int:partido_id>/', admin_views.admin_editar_partido_eliminatoria, name='admin_editar_partido_eliminatoria'),
    path('partidos-eliminatoria/eliminar/<int:partido_id>/', admin_views.admin_eliminar_partido_eliminatoria, name='admin_eliminar_partido_eliminatoria'),

    # Goleadores
    path('goleadores/', admin_views.admin_goleadores, name='admin_goleadores'),
    path('goleadores/crear/', admin_views.admin_crear_goleador, name='admin_crear_goleador'),
    path('goleadores/editar/<int:goleador_id>/', admin_views.admin_editar_goleador, name='admin_editar_goleador'),
    path('goleadores/eliminar/<int:goleador_id>/', admin_views.admin_eliminar_goleador, name='admin_eliminar_goleador'),

    # Herramientas Administrativas
    path('herramientas/', admin_views.admin_herramientas, name='admin_herramientas'),

    # Reportes
    path('panel/reportes/', admin_views.admin_reportes, name='admin_reportes'),

    # Registros de Actividad
    path('panel/actividades/', admin_views.admin_actividades, name='admin_actividades'),

    # AJAX Helpers
    path('panel/ajax/categorias/', admin_views.get_categorias_ajax, name='admin_get_categorias_ajax'),
    path('panel/ajax/equipos/', admin_views.get_equipos_ajax, name='admin_get_equipos_ajax'),
]
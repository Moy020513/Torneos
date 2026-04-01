from django.urls import path, include
from . import views

from .admin_urls import admin_urlpatterns
from .admin_campos_urls import urlpatterns as admin_campos_urlpatterns
from .arbitro_sanciones_view import arbitro_partido_sanciones, arbitro_sancion_editar

urlpatterns = [
    path('', views.index, name='index'),
    path('torneo/<int:torneo_id>/', views.torneo_detalle, name='torneo_detalle'),
    path('categoria/<int:categoria_id>/', views.categoria_detalle, name='categoria_detalle'),
    path('categoria/<int:categoria_id>/eliminatorias/', views.eliminatorias_view, name='eliminatorias'),
    path('categoria/<int:categoria_id>/goleadores/', views.goleadores_view, name='goleadores'),
    path('categoria/<int:categoria_id>/tabla-posiciones/', views.tabla_posiciones_view, name='tabla_posiciones'),
    path('categoria/<int:categoria_id>/equipos/', views.equipos_view, name='equipos'),
    path('categoria/<int:categoria_id>/estadisticas/', views.estadisticas_view, name='estadisticas'),
    path('categoria/<int:categoria_id>/reglamento/', views.reglamento_view, name='reglamento'),
    path('categoria/<int:categoria_id>/resultados/', views.resultados_view, name='resultados'),
    path('categoria/<int:categoria_id>/jornadas-pendientes/', views.jornadas_pendientes_view, name='jornadas_pendientes'),
    path('categoria/<int:categoria_id>/jugadores/', views.jugadores_view, name='jugadores'),
    path('jugador/<int:jugador_id>/', views.jugador_detalle, name='jugador_detalle'),
    path('partido/<int:partido_id>/detalle/', views.partido_detalle, name='partido_detalle'),
    # Perfil
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    # AJAX para admin
    path('get_categorias/', views.get_categorias_by_torneo, name='get_categorias_by_torneo'),
    # URLs de administración (legacy - mantenidas para compatibilidad)
    path('administracion/', views.administracion_dashboard, name='admin_dashboard_legacy'),
    path('administracion/torneo/<int:torneo_id>/', views.administrar_torneo, name='administrar_torneo'),
    path('administracion/generar-calendario/<int:categoria_id>/', views.generar_calendario, name='generar_calendario'),
    # URLs de representantes
        path('representante/', views.representante_panel, name='representante_panel'),
        path('representante/jugadores/crear/', views.representante_jugador_create, name='representante_jugador_create'),
        path('representante/jugadores/<int:jugador_id>/editar/', views.representante_jugador_update, name='representante_jugador_update'),
        path('representante/jugadores/<int:jugador_id>/eliminar/', views.representante_jugador_delete, name='representante_jugador_delete'),
        path('equipo/<int:equipo_id>/gestion/', views.gestion_equipo, name='gestion_equipo'),
        # Panel de árbitro
        path('arbitro/', views.arbitro_panel, name='arbitro_panel'),
           path('arbitro/partido/<int:partido_id>/resultado/', views.arbitro_partido_resultado, name='arbitro_partido_resultado'),
           path('arbitro/partido/<int:partido_id>/goleadores/',
               __import__('torneos.arbitro_goleadores_view').arbitro_goleadores_view.arbitro_partido_goleadores,
               name='arbitro_partido_goleadores'),
           path('arbitro/partido/<int:partido_id>/goleadores/<int:jugador_id>/editar/',
               __import__('torneos.arbitro_goleadores_view').arbitro_goleadores_view.arbitro_goleador_editar,
               name='arbitro_goleador_editar'),
        path('arbitro/partido/<int:partido_id>/resultado/eliminar/', views.arbitro_partido_eliminar_resultado, name='arbitro_partido_eliminar_resultado'),
        path('arbitro/partido/<int:partido_id>/participaciones/', views.arbitro_partido_participaciones, name='arbitro_partido_participaciones'),
        path('arbitro/partido/<int:partido_id>/participaciones/agregar/', views.arbitro_participacion_agregar, name='arbitro_participacion_agregar'),
        path('arbitro/participacion/<int:participacion_id>/eliminar/', views.arbitro_participacion_eliminar, name='arbitro_participacion_eliminar'),
    path('arbitro/partido/<int:partido_id>/sanciones/', arbitro_partido_sanciones, name='arbitro_partido_sanciones'),
    path('arbitro/partido/<int:partido_id>/sanciones/<int:jugador_id>/editar/', arbitro_sancion_editar, name='arbitro_sancion_editar'),
    path('categoria/<int:categoria_id>/sanciones/', views.torneo_sanciones_view, name='torneo_sanciones'),
] + admin_urlpatterns + admin_campos_urlpatterns
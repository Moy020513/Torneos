from django.urls import path, include
from . import views

from .admin_urls import admin_urlpatterns
from .admin_campos_urls import urlpatterns as admin_campos_urlpatterns

urlpatterns = [
    path('', views.index, name='index'),
    path('torneo/<int:torneo_id>/', views.torneo_detalle, name='torneo_detalle'),
    path('categoria/<int:categoria_id>/', views.categoria_detalle, name='categoria_detalle'),
    path('categoria/<int:categoria_id>/eliminatorias/', views.eliminatorias_view, name='eliminatorias'),
    path('categoria/<int:categoria_id>/goleadores/', views.goleadores_view, name='goleadores'),
    path('categoria/<int:categoria_id>/tabla-posiciones/', views.tabla_posiciones_view, name='tabla_posiciones'),
    path('categoria/<int:categoria_id>/equipos/', views.equipos_view, name='equipos'),
    path('categoria/<int:categoria_id>/estadisticas/', views.estadisticas_view, name='estadisticas'),
    path('categoria/<int:categoria_id>/resultados/', views.resultados_view, name='resultados'),
    path('categoria/<int:categoria_id>/jugadores/', views.jugadores_view, name='jugadores'),
    # AJAX para admin
    path('get_categorias/', views.get_categorias_by_torneo, name='get_categorias_by_torneo'),
    # URLs de administración (legacy - mantenidas para compatibilidad)
    path('administracion/', views.administracion_dashboard, name='admin_dashboard_legacy'),
    path('administracion/torneo/<int:torneo_id>/', views.administrar_torneo, name='administrar_torneo'),
    path('administracion/generar-calendario/<int:categoria_id>/', views.generar_calendario, name='generar_calendario'),
    # URLs de capitanes
        path('capitan/', views.capitan_panel, name='capitan_panel'),
        path('capitan/jugadores/crear/', views.capitan_jugador_create, name='capitan_jugador_create'),
        path('capitan/jugadores/<int:jugador_id>/editar/', views.capitan_jugador_update, name='capitan_jugador_update'),
        path('capitan/jugadores/<int:jugador_id>/eliminar/', views.capitan_jugador_delete, name='capitan_jugador_delete'),
        path('equipo/<int:equipo_id>/gestion/', views.gestion_equipo, name='gestion_equipo'),
] + admin_urlpatterns + admin_campos_urlpatterns
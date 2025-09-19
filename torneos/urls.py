from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('torneo/<int:torneo_id>/', views.torneo_detalle, name='torneo_detalle'),
    path('categoria/<int:categoria_id>/', views.categoria_detalle, name='categoria_detalle'),
    path('categoria/<int:categoria_id>/eliminatorias/', views.eliminatorias_view, name='eliminatorias'),
    path('categoria/<int:categoria_id>/goleadores/', views.goleadores_view, name='goleadores'),
    
    # URLs de administración
    path('administracion/', views.administracion_dashboard, name='admin_dashboard'),
    path('administracion/torneo/<int:torneo_id>/', views.administrar_torneo, name='administrar_torneo'),
    path('administracion/generar-calendario/<int:categoria_id>/', views.generar_calendario, name='generar_calendario'),
    
    # URLs de capitanes
    path('equipo/<int:equipo_id>/gestion/', views.gestion_equipo, name='gestion_equipo'),
]
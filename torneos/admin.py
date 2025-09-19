
from django.contrib import admin
from .models import Eliminatoria, Torneo, Categoria, Equipo, Jugador, Capitan, Partido, PartidoEliminatoria, Goleador
from .forms import EquipoAdminForm

@admin.register(Eliminatoria)
class EliminatoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'orden')
    list_filter = ('categoria', 'nombre')
    search_fields = ('nombre',)

@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'formato_torneo', 'activo')
    list_filter = ('activo', 'formato_torneo')
    search_fields = ('nombre', 'descripcion')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'torneo', 'max_equipos', 'tiene_eliminatorias')
    list_filter = ('torneo', 'tiene_eliminatorias')
    search_fields = ('nombre', 'descripcion')

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    form = EquipoAdminForm
    list_display = ('nombre', 'categoria', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre',)

@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'equipo', 'numero_camiseta', 'posicion', 'activo')
    list_filter = ('equipo', 'posicion', 'activo')
    search_fields = ('nombre', 'apellido')

@admin.register(Capitan)
class CapitanAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'equipo', 'activo')
    list_filter = ('activo',)
    search_fields = ('usuario__username', 'equipo__nombre')

@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ('equipo_local', 'equipo_visitante', 'jornada', 'goles_local', 'goles_visitante', 'jugado')
    list_filter = ('grupo', 'jornada', 'jugado')
    search_fields = ('equipo_local__nombre', 'equipo_visitante__nombre')

@admin.register(PartidoEliminatoria)
class PartidoEliminatoriaAdmin(admin.ModelAdmin):
    list_display = ('equipo_local', 'equipo_visitante', 'eliminatoria', 'goles_local', 'goles_visitante', 'jugado')
    list_filter = ('eliminatoria', 'jugado')
    search_fields = ('equipo_local__nombre', 'equipo_visitante__nombre')

@admin.register(Goleador)
class GoleadorAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'partido', 'partido_eliminatoria', 'goles')
    list_filter = ('partido', 'partido_eliminatoria')
    search_fields = ('jugador__nombre', 'jugador__apellido')
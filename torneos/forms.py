
from django import forms
from .models import *

class EquipoAdminForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = '__all__'
        widgets = {
            'color_principal': forms.TextInput(attrs={'type': 'color'}),
            'color_secundario': forms.TextInput(attrs={'type': 'color'}),
        }

class GoleadorForm(forms.ModelForm):
    class Meta:
        model = Goleador
        fields = ['jugador', 'partido', 'partido_eliminatoria', 'categoria', 'goles']

class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = ['nombre', 'apellido', 'foto', 'fecha_nacimiento', 'numero_camiseta', 'posicion']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['nombre', 'logo', 'color_principal', 'color_secundario']
        widgets = {
            'color_principal': forms.TextInput(attrs={'type': 'color'}),
            'color_secundario': forms.TextInput(attrs={'type': 'color'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'max_equipos', 'tiene_eliminatorias', 'num_equipos_eliminatoria']

class TorneoForm(forms.ModelForm):
    class Meta:
        model = Torneo
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'formato_torneo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

class PartidoForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['goles_local', 'goles_visitante', 'jugado', 'campo']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class PartidoEliminatoriaForm(forms.ModelForm):
    class Meta:
        model = PartidoEliminatoria
        fields = ['goles_local', 'goles_visitante', 'goles_local_vuelta', 'goles_visitante_vuelta', 'jugado', 'campo']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
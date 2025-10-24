# Importar forms y modelos antes de definir formularios que los usan
from django import forms
from .models import *
# Formulario para registrar participaciones múltiples
class ParticipacionMultipleForm(forms.Form):
    equipo = forms.ModelChoiceField(queryset=Equipo.objects.all(), label='Equipo')
    jugadores = forms.ModelMultipleChoiceField(queryset=Jugador.objects.none(), widget=forms.CheckboxSelectMultiple, label='Jugadores')
    partido = forms.ModelChoiceField(queryset=Partido.objects.none(), label='Partido')

    def __init__(self, *args, **kwargs):
        equipo_id = kwargs.pop('equipo_id', None)
        super().__init__(*args, **kwargs)
        if equipo_id:
            self.fields['jugadores'].queryset = Jugador.objects.filter(equipo_id=equipo_id)
            # Mostrar sólo partidos en los que participa el equipo y que ya fueron jugados
            self.fields['partido'].queryset = Partido.objects.filter(
                (models.Q(equipo_local__id=equipo_id) | models.Q(equipo_visitante__id=equipo_id)),
                jugado=True
            )
            # Establecer el valor inicial del campo equipo si no viene en POST
            if not self.data.get('equipo'):
                self.initial['equipo'] = equipo_id
        else:
            self.fields['jugadores'].queryset = Jugador.objects.none()
            self.fields['partido'].queryset = Partido.objects.none()

from django import forms
from django.contrib.auth.models import User
from .models import *

# Mixin para aplicar clases CSS consistentes a todos los formularios del admin
class AdminFormMixin:
    """Mixin para aplicar clases CSS consistentes a todos los formularios del admin"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.widgets.Select):
                field.widget.attrs.update({'class': 'admin-form-control form-select'})
            elif isinstance(field.widget, forms.widgets.FileInput):
                field.widget.attrs.update({'class': 'admin-form-control form-control'})
            else:
                field.widget.attrs.update({'class': 'admin-form-control form-control'})

# Formulario para ParticipacionJugador en el panel admin personalizado
class ParticipacionJugadorForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = ParticipacionJugador
        fields = ['jugador', 'partido', 'titular', 'minutos_jugados', 'observaciones']
        labels = {
            'jugador': 'Jugador',
            'partido': 'Partido',
            'titular': '¿Fue titular?',
            'minutos_jugados': 'Minutos jugados',
            'observaciones': 'Observaciones',
        }



class TorneoForm(AdminFormMixin, forms.ModelForm):
    # Eliminar la asignación manual de value; dejar que Django maneje los valores de fecha
    class Meta:
        model = Torneo
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'formato_torneo', 'logo', 'activo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'nombre': 'Nombre del Torneo',
            'descripcion': 'Descripción',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Finalización',
            'formato_torneo': 'Formato del Torneo',
            'logo': 'Logo del Torneo',
            'activo': 'Torneo Activo',
        }

class CategoriaForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['torneo', 'nombre', 'descripcion', 'max_equipos', 'tiene_eliminatorias', 'num_equipos_eliminatoria']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'torneo': 'Torneo',
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción',
            'max_equipos': 'Máximo de Equipos',
            'tiene_eliminatorias': 'Incluye Fase Eliminatoria',
            'num_equipos_eliminatoria': 'Equipos en Eliminatorias',
        }

class EquipoForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['categoria', 'nombre', 'logo', 'color_principal', 'color_secundario', 'activo']
        widgets = {
            'color_principal': forms.TextInput(attrs={'type': 'color'}),
            'color_secundario': forms.TextInput(attrs={'type': 'color'}),
        }
        labels = {
            'categoria': 'Categoría',
            'nombre': 'Nombre del Equipo',
            'logo': 'Logo del Equipo',
            'color_principal': 'Color Principal',
            'color_secundario': 'Color Secundario',
            'activo': 'Equipo Activo',
        }


# Formulario para el panel de administración
class JugadorForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Jugador
        # No exponer el campo 'activo' para que los jugadores siempre queden activos al registrarse
        fields = ['equipo', 'nombre', 'apellido', 'foto', 'fecha_nacimiento', 'numero_camiseta', 'posicion', 'verificado']
        widgets = {
            # Usar formato compatible con input[type=date] (YYYY-MM-DD)
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        labels = {
            'equipo': 'Equipo',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'foto': 'Foto del Jugador',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'numero_camiseta': 'Número de Camiseta',
            'posicion': 'Posición',
            'verificado': 'Verificado por Admin',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si viene una instancia con fecha_nacimiento, formatearla para que el input[type=date] la muestre correctamente
        instance = getattr(self, 'instance', None)
        if instance and getattr(instance, 'fecha_nacimiento', None):
            try:
                self.fields['fecha_nacimiento'].initial = instance.fecha_nacimiento.strftime('%Y-%m-%d')
            except Exception:
                pass

# Formulario para el capitán (sin campo equipo)
class CapitanJugadorForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Jugador
        # Los capitanes no pueden inactivar jugadores desde su formulario
        fields = ['nombre', 'apellido', 'foto', 'fecha_nacimiento', 'numero_camiseta', 'posicion']
        widgets = {
            'nombre': forms.TextInput(attrs={'style': 'text-transform:uppercase;', 'oninput': "this.value = this.value.toUpperCase();"}),
            'apellido': forms.TextInput(attrs={'style': 'text-transform:uppercase;', 'oninput': "this.value = this.value.toUpperCase();"}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
        labels = {
            'nombre': 'Nombre(s)',
            'apellido': 'Apellidos',
            'foto': 'Foto del Jugador',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'numero_camiseta': 'Número de Camiseta',
            'posicion': 'Posición',
            
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and getattr(instance, 'fecha_nacimiento', None):
            try:
                self.fields['fecha_nacimiento'].initial = instance.fecha_nacimiento.strftime('%Y-%m-%d')
            except Exception:
                pass


class PartidoForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['grupo', 'jornada', 'equipo_local', 'equipo_visitante', 'fecha', 'goles_local', 'goles_visitante', 'jugado', 'ubicacion']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        labels = {
            'grupo': 'Grupo',
            'jornada': 'Jornada',
            'equipo_local': 'Equipo Local',
            'equipo_visitante': 'Equipo Visitante',
            'fecha': 'Fecha y Hora',
            'goles_local': 'Goles Equipo Local',
            'goles_visitante': 'Goles Equipo Visitante',
            'jugado': 'Partido Jugado',
            'ubicacion': 'Campo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.fecha:
            self.fields['fecha'].initial = self.instance.fecha.strftime('%Y-%m-%dT%H:%M')

class UsuarioForm(AdminFormMixin, forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(), 
        required=True,
        help_text='Ingrese una contraseña segura'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(), 
        required=True,
        label='Confirmar Contraseña'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser']
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'is_active': 'Usuario Activo',
            'is_staff': 'Acceso al Admin',
            'is_superuser': 'Superusuario',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user

# Formularios originales (mantenidos para compatibilidad)
class EquipoAdminForm(forms.ModelForm):
    torneo = forms.ModelChoiceField(queryset=Torneo.objects.all(), required=False, label='Torneo')

    class Meta:
        model = Equipo
        fields = ['torneo', 'categoria', 'nombre', 'logo', 'color_principal', 'color_secundario', 'activo']
        widgets = {
            'color_principal': forms.TextInput(attrs={'type': 'color'}),
            'color_secundario': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si hay torneo seleccionado, filtrar categorías
        if self.data.get('torneo'):
            try:
                torneo_id = int(self.data.get('torneo'))
                self.fields['categoria'].queryset = Categoria.objects.filter(torneo_id=torneo_id)
            except (ValueError, TypeError):
                self.fields['categoria'].queryset = Categoria.objects.none()
        elif self.instance.pk and self.instance.categoria:
            torneo = self.instance.categoria.torneo
            self.fields['categoria'].queryset = Categoria.objects.filter(torneo=torneo)
            self.fields['torneo'].initial = torneo
        else:
            self.fields['categoria'].queryset = Categoria.objects.none()

class GoleadorForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Goleador
        fields = ['jugador', 'partido', 'partido_eliminatoria', 'categoria', 'goles']
        labels = {
            'jugador': 'Jugador',
            'partido': 'Partido Regular',
            'partido_eliminatoria': 'Partido Eliminatoria',
            'categoria': 'Categoría',
            'goles': 'Número de Goles',
        }
        help_texts = {
            'partido': 'Seleccione el partido regular (opcional si es eliminatoria)',
            'partido_eliminatoria': 'Seleccione el partido eliminatoria (opcional si es regular)',
            'goles': 'Número de goles anotados por el jugador en este partido',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        partido = cleaned_data.get('partido')
        partido_eliminatoria = cleaned_data.get('partido_eliminatoria')
        
        # Validar que se seleccione al menos un partido
        if not partido and not partido_eliminatoria:
            raise forms.ValidationError('Debe seleccionar un partido regular o un partido de eliminatoria.')
        
        # Validar que no se seleccionen ambos
        if partido and partido_eliminatoria:
            raise forms.ValidationError('No puede seleccionar tanto un partido regular como un partido de eliminatoria.')
        
        return cleaned_data

class PartidoEliminatoriaForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = PartidoEliminatoria
        fields = ['eliminatoria', 'equipo_local', 'equipo_visitante', 'fecha', 'goles_local', 'goles_visitante', 'goles_local_vuelta', 'goles_visitante_vuelta', 'jugado', 'campo']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'eliminatoria': 'Eliminatoria',
            'equipo_local': 'Equipo Local',
            'equipo_visitante': 'Equipo Visitante', 
            'fecha': 'Fecha y Hora',
            'goles_local': 'Goles Local (Ida)',
            'goles_visitante': 'Goles Visitante (Ida)',
            'goles_local_vuelta': 'Goles Local (Vuelta)',
            'goles_visitante_vuelta': 'Goles Visitante (Vuelta)',
            'jugado': 'Partido Jugado',
            'campo': 'Campo de Juego',
        }

# Formularios adicionales para las nuevas secciones

class GrupoForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['categoria', 'nombre', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'categoria': 'Categoría',
            'nombre': 'Nombre del Grupo',
            'descripcion': 'Descripción',
        }

class UsuarioEditForm(AdminFormMixin, forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(), 
        required=False,
        help_text='Deje en blanco para mantener la contraseña actual'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(), 
        required=False,
        label='Confirmar Contraseña'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser']
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'is_active': 'Usuario Activo',
            'is_staff': 'Acceso al Admin',
            'is_superuser': 'Superusuario',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and password != confirm_password:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user

class CapitanForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Capitan
        fields = ['usuario', 'equipo', 'activo']
        labels = {
            'usuario': 'Usuario',
            'equipo': 'Equipo',
            'activo': 'Capitán Activo',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.db.models import Q
        
        # Filtrar usuarios que no son capitanes (excepto si estamos editando)
        if self.instance and self.instance.pk:
            # Al editar, incluir el usuario actual
            usuarios_sin_capitan = User.objects.filter(
                Q(capitan__isnull=True) | Q(id=self.instance.usuario.id)
            )
        else:
            # Al crear, solo usuarios sin capitanía
            usuarios_sin_capitan = User.objects.filter(capitan__isnull=True)
        
        self.fields['usuario'].queryset = usuarios_sin_capitan
        
        # Filtrar equipos que no tienen capitán (excepto si estamos editando)
        if self.instance and self.instance.pk:
            equipos_sin_capitan = Equipo.objects.filter(
                Q(capitan__isnull=True) | Q(id=self.instance.equipo.id)
            )
        else:
            equipos_sin_capitan = Equipo.objects.filter(capitan__isnull=True)
        
        self.fields['equipo'].queryset = equipos_sin_capitan

class EliminatoriaForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Eliminatoria
        fields = ['categoria', 'nombre', 'orden']
        labels = {
            'categoria': 'Categoría',
            'nombre': 'Fase de Eliminatoria',
            'orden': 'Orden de Ejecución',
        }
        help_texts = {
            'orden': 'Número que determina el orden de las fases (1=Primera, 2=Segunda, etc.)',
        }
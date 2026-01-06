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
        # Permitir pasar assigned_torneo (id) para limitar equipos disponibles
        assigned_torneo = kwargs.pop('assigned_torneo', None)
        super().__init__(*args, **kwargs)
        # Limitar el queryset del campo 'equipo' si se proporciona assigned_torneo
        if assigned_torneo:
            try:
                self.fields['equipo'].queryset = Equipo.objects.filter(categoria__torneo_id=assigned_torneo)
            except Exception:
                self.fields['equipo'].queryset = Equipo.objects.none()

        if equipo_id:
            # Ordenar jugadores alfabéticamente por nombre y apellido
            self.fields['jugadores'].queryset = Jugador.objects.filter(equipo_id=equipo_id).order_by('nombre', 'apellido')
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
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'formato_torneo', 'logo', 'reglamento', 'activo']
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
            'reglamento': 'Reglamento (archivo)',
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

    def __init__(self, *args, **kwargs):
        """Permite pasar assigned_torneo (id) para restringir y deshabilitar el campo torneo.

        Si se pasa assigned_torneo (int), el campo 'torneo' queda con queryset solo de ese torneo,
        se establece el valor inicial y se deshabilita el widget para impedir cambios desde UI.
        Como los campos deshabilitados no se incluyen en POST, no confíes en que vengan en cleaned_data;
        la vista que crea/edita debe forzar el torneo antes de guardar cuando corresponda.
        """
        assigned_torneo = kwargs.pop('assigned_torneo', None)
        super().__init__(*args, **kwargs)

        # Si nos pasan un torneo asignado, limitar las opciones y deshabilitar selector
        if assigned_torneo:
            try:
                from .models import Torneo
                torneo_qs = Torneo.objects.filter(id=assigned_torneo)
                self.fields['torneo'].queryset = torneo_qs
                # Establecer initial si hay exactamente uno
                if torneo_qs.exists():
                    self.initial['torneo'] = torneo_qs.first()
                # Deshabilitar el campo en la UI (no editable)
                self.fields['torneo'].widget.attrs.update({'disabled': 'disabled'})
                # No exigir su presencia en POST ya que estará ausente cuando esté deshabilitado
                self.fields['torneo'].required = False
            except Exception:
                pass

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

    def __init__(self, *args, **kwargs):
        """Limitar el queryset de 'categoria' cuando se pasa assigned_torneo (id).

        Si assigned_torneo es proporcionado, solo se mostrarán categorías de ese torneo.
        """
        assigned_torneo = kwargs.pop('assigned_torneo', None)
        super().__init__(*args, **kwargs)

        # Si se pasó assigned_torneo, limitar opciones
        if assigned_torneo:
            try:
                self.fields['categoria'].queryset = Categoria.objects.filter(torneo_id=assigned_torneo)
            except Exception:
                # En caso de error, dejar la queryset por defecto
                self.fields['categoria'].queryset = Categoria.objects.none()
        else:
            # Si ya existe una instancia con categoria, dejar al menos esa opción
            if self.instance and getattr(self.instance, 'categoria', None):
                torneo = self.instance.categoria.torneo
                self.fields['categoria'].queryset = Categoria.objects.filter(torneo=torneo)
            else:
                self.fields['categoria'].queryset = Categoria.objects.all()


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
        """Permite pasar assigned_torneo (id) para mostrar solo equipos del torneo asignado.

        Si assigned_torneo se proporciona, el queryset del campo 'equipo' se limitará
        a los equipos cuyas categorías pertenecen a ese torneo. También se intenta
        mantener comportamiento razonable al editar una instancia existente.
        """
        assigned_torneo = kwargs.pop('assigned_torneo', None)
        super().__init__(*args, **kwargs)

        # Limitar el queryset de 'equipo' según el torneo asignado cuando corresponda
        if assigned_torneo:
            try:
                self.fields['equipo'].queryset = Equipo.objects.filter(categoria__torneo_id=assigned_torneo)
            except Exception:
                self.fields['equipo'].queryset = Equipo.objects.none()
        else:
            # Si estamos editando y la instancia tiene equipo, limitar al torneo de ese equipo
            if self.instance and getattr(self.instance, 'equipo', None):
                try:
                    equipo = self.instance.equipo
                    torneo = equipo.categoria.torneo
                    self.fields['equipo'].queryset = Equipo.objects.filter(categoria=torneo)
                except Exception:
                    self.fields['equipo'].queryset = Equipo.objects.all()
            else:
                self.fields['equipo'].queryset = Equipo.objects.all()

        # Si viene una instancia con fecha_nacimiento, formatearla para que el input[type=date] la muestre correctamente
        instance = getattr(self, 'instance', None)
        if instance and getattr(instance, 'fecha_nacimiento', None):
            try:
                self.fields['fecha_nacimiento'].initial = instance.fecha_nacimiento.strftime('%Y-%m-%d')
            except Exception:
                pass

# Formulario para el representante (sin campo equipo)
class RepresentanteJugadorForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Jugador
        # Los representantees no pueden inactivar jugadores desde su formulario
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
        fields = ['grupo', 'jornada', 'equipo_local', 'equipo_visitante', 'fecha', 'goles_local', 'goles_visitante', 'jugado', 'arbitro', 'ubicacion']
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
            'arbitro': 'Árbitro asignado',
            'ubicacion': 'Campo',
        }

    def __init__(self, *args, **kwargs):
        # Permitir pasar assigned_torneo para limitar grupos y equipos al torneo asignado
        assigned_torneo = kwargs.pop('assigned_torneo', None)
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        # Limitar los querysets de grupo y equipos cuando corresponda
        if assigned_torneo:
            try:
                self.fields['grupo'].queryset = Grupo.objects.filter(categoria__torneo_id=assigned_torneo)
            except Exception:
                self.fields['grupo'].queryset = Grupo.objects.none()
            try:
                equipos_qs = Equipo.objects.filter(categoria__torneo_id=assigned_torneo)
                self.fields['equipo_local'].queryset = equipos_qs
                self.fields['equipo_visitante'].queryset = equipos_qs
            except Exception:
                self.fields['equipo_local'].queryset = Equipo.objects.none()
                self.fields['equipo_visitante'].queryset = Equipo.objects.none()
            try:
                from .models import Arbitro
                self.fields['arbitro'].queryset = Arbitro.objects.filter(torneo_id=assigned_torneo)
            except Exception:
                self.fields['arbitro'].queryset = Arbitro.objects.none()
            # Limitar ubicaciones a aquellas asociadas al torneo (si existieran)
            try:
                from django.db.models import Q
                ubicaciones_qs = UbicacionCampo.objects.filter(
                    Q(partidos__grupo__categoria__torneo_id=assigned_torneo) |
                    Q(partidos__equipo_local__categoria__torneo_id=assigned_torneo) |
                    Q(partidos__equipo_visitante__categoria__torneo_id=assigned_torneo)
                )
                if current_user and not getattr(current_user, 'is_superuser', False):
                    ubicaciones_qs = ubicaciones_qs | UbicacionCampo.objects.filter(creado_por=current_user)
                self.fields['ubicacion'].queryset = ubicaciones_qs.distinct()
            except Exception:
                self.fields['ubicacion'].queryset = UbicacionCampo.objects.none()
        else:
            try:
                from .models import Arbitro
                arbitro_field = self.fields.get('arbitro')
                if arbitro_field is not None:
                    if self.instance and getattr(self.instance, 'grupo', None):
                        torneo_id = self.instance.grupo.categoria.torneo_id
                        arbitro_field.queryset = Arbitro.objects.filter(models.Q(torneo_id=torneo_id) | models.Q(id=getattr(self.instance, 'arbitro_id', None)))
                    else:
                        arbitro_field.queryset = Arbitro.objects.all()
            except Exception:
                arbitro_field = self.fields.get('arbitro')
                if arbitro_field is not None:
                    arbitro_field.queryset = arbitro_field.queryset.none()
            # Si estamos editando, asegurar que los equipos actuales estén incluidos en la queryset
            if self.instance and getattr(self.instance, 'equipo_local', None):
                try:
                    equipo = self.instance.equipo_local
                    self.fields['equipo_local'].queryset = Equipo.objects.filter(categoria=equipo.categoria)
                except Exception:
                    self.fields['equipo_local'].queryset = Equipo.objects.all()
            else:
                self.fields['equipo_local'].queryset = Equipo.objects.all()

            if self.instance and getattr(self.instance, 'equipo_visitante', None):
                try:
                    equipo = self.instance.equipo_visitante
                    self.fields['equipo_visitante'].queryset = Equipo.objects.filter(categoria=equipo.categoria)
                except Exception:
                    self.fields['equipo_visitante'].queryset = Equipo.objects.all()
            else:
                self.fields['equipo_visitante'].queryset = Equipo.objects.all()

            if self.instance and getattr(self.instance, 'grupo', None):
                try:
                    grupo = self.instance.grupo
                    self.fields['grupo'].queryset = Grupo.objects.filter(categoria=grupo.categoria)
                except Exception:
                    self.fields['grupo'].queryset = Grupo.objects.all()
            else:
                self.fields['grupo'].queryset = Grupo.objects.all()

        if self.instance and self.instance.fecha:
            self.fields['fecha'].initial = self.instance.fecha.strftime('%Y-%m-%dT%H:%M')


class ArbitroResultadoForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['goles_local', 'goles_visitante', 'jugado']
        labels = {
            'goles_local': 'Goles equipo local',
            'goles_visitante': 'Goles equipo visitante',
            'jugado': 'Marcar como finalizado',
        }
        widgets = {
            'goles_local': forms.NumberInput(attrs={'min': 0}),
            'goles_visitante': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marcar jugado como verdadero por defecto cuando se abre el formulario
        if not self.initial.get('jugado', None):
            self.initial['jugado'] = True

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

    def __init__(self, *args, **kwargs):
        """Si restrict_privileges=True, ocultar/deshabilitar campos de privilegios.

        Esto se usa para que administradores de torneo no vean ni puedan asignar
        is_staff/is_superuser al crear usuarios.
        """
        restrict_privileges = kwargs.pop('restrict_privileges', False)
        super().__init__(*args, **kwargs)
        if restrict_privileges:
            # Quitar los campos por completo para que no sean visibles en la plantilla
            self.fields.pop('is_staff', None)
            self.fields.pop('is_superuser', None)

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

    def __init__(self, *args, **kwargs):
        """Si restrict_privileges=True, deshabilitar campos is_staff/is_superuser en la UI.

        No cambia el comportamiento de guardado; se usa para evitar que administradores
        asignados intenten promover usuarios.
        """
        restrict_privileges = kwargs.pop('restrict_privileges', False)
        super().__init__(*args, **kwargs)
        if restrict_privileges:
            # Quitar los campos por completo para que no aparezcan al editar
            self.fields.pop('is_staff', None)
            self.fields.pop('is_superuser', None)

class ArbitroForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Arbitro
        fields = ['usuario', 'torneo', 'activo']
        labels = {
            'usuario': 'Usuario',
            'torneo': 'Torneo',
            'activo': 'Árbitro activo',
        }

    def __init__(self, *args, **kwargs):
        created_by = kwargs.pop('created_by', None)
        assigned_torneo = kwargs.pop('assigned_torneo', None)
        super().__init__(*args, **kwargs)
        from django.db.models import Q

        if self.instance and self.instance.pk:
            usuarios_qs = User.objects.filter(Q(arbitro__isnull=True) | Q(id=self.instance.usuario_id))
        else:
            usuarios_qs = User.objects.filter(arbitro__isnull=True)

        if created_by:
            try:
                from .models import UsuarioCreado
                usuarios_ids = list(UsuarioCreado.objects.filter(creado_por=created_by).values_list('usuario_id', flat=True))
                if self.instance and getattr(self.instance, 'usuario_id', None):
                    usuarios_ids = list(set(usuarios_ids) | {self.instance.usuario_id})
                if usuarios_ids:
                    usuarios_qs = usuarios_qs.filter(id__in=usuarios_ids)
                else:
                    usuarios_qs = User.objects.none()
            except Exception:
                pass

        self.fields['usuario'].queryset = usuarios_qs

        if assigned_torneo:
            try:
                torneo_qs = Torneo.objects.filter(id=assigned_torneo)
                self.fields['torneo'].queryset = torneo_qs
                if torneo_qs.exists():
                    self.initial['torneo'] = torneo_qs.first()
                self.fields['torneo'].widget.attrs.update({'disabled': 'disabled'})
                self.fields['torneo'].required = False
            except Exception:
                pass

class RepresentanteForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Representante
        fields = ['usuario', 'equipo', 'activo']
        labels = {
            'usuario': 'Usuario',
            'equipo': 'Equipo',
            'activo': 'Representante Activo',
        }
    
    def __init__(self, *args, **kwargs):
        # Permitir restringir usuarios a los creados por un administrador
        created_by = kwargs.pop('created_by', None)
        super().__init__(*args, **kwargs)
        from django.db.models import Q
        
        # Filtrar usuarios que no son representantees (excepto si estamos editando)
        if self.instance and self.instance.pk:
            # Al editar, incluir el usuario actual
            usuarios_sin_representante = User.objects.filter(
                Q(representante__isnull=True) | Q(id=self.instance.usuario.id)
            )
        else:
            # Al crear, solo usuarios sin representanteía
            usuarios_sin_representante = User.objects.filter(representante__isnull=True)

        # Si se pasa created_by (usuario que creó usuarios), limitar a los usuarios creados por él
        if created_by:
            try:
                from .models import UsuarioCreado
                usuarios_ids = list(UsuarioCreado.objects.filter(creado_por=created_by).values_list('usuario_id', flat=True))
                # Si estamos editando, asegurarnos de permitir el usuario actual aunque no esté en la lista
                if self.instance and getattr(self.instance, 'usuario', None):
                    usuarios_ids = list(set(usuarios_ids) | {self.instance.usuario.id})
                if usuarios_ids:
                    usuarios_sin_representante = usuarios_sin_representante.filter(id__in=usuarios_ids)
                else:
                    # No hay usuarios creados por ese admin -> queryset vacía
                    usuarios_sin_representante = User.objects.none()
            except Exception:
                # En caso de error, no aplicar la restricción adicional
                pass

        self.fields['usuario'].queryset = usuarios_sin_representante
        
        # Filtrar equipos que no tienen representante (excepto si estamos editando)
        if self.instance and self.instance.pk:
            equipos_sin_representante = Equipo.objects.filter(
                Q(representante__isnull=True) | Q(id=self.instance.equipo.id)
            )
        else:
            equipos_sin_representante = Equipo.objects.filter(representante__isnull=True)
        
        self.fields['equipo'].queryset = equipos_sin_representante

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


class AjustePuntosForm(AdminFormMixin, forms.ModelForm):
    """Formulario para ajustar puntos de equipos en la tabla de clasificación"""
    class Meta:
        model = AjustePuntos
        fields = ['equipo', 'categoria', 'puntos_ajuste', 'razon']
        labels = {
            'equipo': 'Equipo',
            'categoria': 'Categoría',
            'puntos_ajuste': 'Puntos a Ajustar',
            'razon': 'Razón del Ajuste',
        }
        help_texts = {
            'puntos_ajuste': 'Use números positivos para agregar puntos, negativos para quitar',
            'razon': 'Ej: Penalización, corrección manual, etc.',
        }
        widgets = {
            'equipo': forms.Select(attrs={'class': 'admin-form-control form-select'}),
            'categoria': forms.Select(attrs={'class': 'admin-form-control form-select'}),
            'puntos_ajuste': forms.NumberInput(attrs={'class': 'admin-form-control', 'placeholder': 'Ej: 3 o -1'}),
            'razon': forms.TextInput(attrs={'class': 'admin-form-control', 'placeholder': 'Motivo del ajuste'}),
        }
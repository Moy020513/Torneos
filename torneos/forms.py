
from django import forms
from django.contrib.auth.models import User
from .models import *

class AdministradorTorneoForm(forms.ModelForm):
    class Meta:
        model = AdministradorTorneo
        fields = ['usuario', 'torneo', 'activo']

# Formularios para el Panel de Administración
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

class TorneoForm(AdminFormMixin, forms.ModelForm):
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
        fields = ['equipo', 'nombre', 'apellido', 'foto', 'fecha_nacimiento', 'numero_camiseta', 'posicion', 'activo']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'equipo': 'Equipo',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'foto': 'Foto del Jugador',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'numero_camiseta': 'Número de Camiseta',
            'posicion': 'Posición',
            'activo': 'Jugador Activo',
        }

# Formulario para el capitán (sin campo equipo)
class CapitanJugadorForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Jugador
        fields = ['nombre', 'apellido', 'foto', 'fecha_nacimiento', 'numero_camiseta', 'posicion', 'activo']
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
            'activo': 'Jugador Activo',
        }


class PartidoForm(AdminFormMixin, forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['grupo', 'jornada', 'equipo_local', 'equipo_visitante', 'fecha', 'goles_local', 'goles_visitante', 'jugado', 'campo']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
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
            'campo': 'Campo de Juego',
        }

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = kwargs.get('request')
        # Si el usuario actual no es superuser/staff, ocultar los campos de staff y superuser
        if hasattr(self, 'current_user') and not (self.current_user.is_superuser or self.current_user.is_staff):
            self.fields.pop('is_staff', None)
            self.fields.pop('is_superuser', None)
    
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
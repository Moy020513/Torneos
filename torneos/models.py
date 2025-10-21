from django.db import models

class ParticipacionJugador(models.Model):
    jugador = models.ForeignKey('Jugador', on_delete=models.CASCADE, related_name='participaciones')
    partido = models.ForeignKey('Partido', on_delete=models.CASCADE, related_name='participaciones')
    titular = models.BooleanField(default=True, help_text='¿Fue titular?')
    minutos_jugados = models.PositiveIntegerField(null=True, blank=True)
    observaciones = models.CharField(max_length=255, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('jugador', 'partido')
        verbose_name = 'Participación de Jugador'
        verbose_name_plural = 'Participaciones de Jugadores'

    def __str__(self):
        return f"{self.jugador} en {self.partido}"
class UbicacionCampo(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.nombre
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from PIL import Image
import os

class Torneo(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    formato_torneo = models.CharField(max_length=50, choices=[
        ('liga', 'Liga'),
        ('eliminatoria', 'Eliminatoria'),
        ('mixto', 'Mixto (Liga + Eliminatoria)')
    ])
    logo = models.ImageField(
        upload_to='torneos/logos/', 
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
        blank=True, 
        null=True
    )
    color1 = models.CharField(max_length=7, blank=True, null=True)
    color2 = models.CharField(max_length=7, blank=True, null=True)
    color3 = models.CharField(max_length=7, blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.logo:
            img = Image.open(self.logo.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
            # Extraer colores principales únicos
            img_rgb = img.convert('RGB')
            img_quant = img_rgb.quantize(colors=256)
            colors = img_quant.getcolors()
            palette = img_quant.getpalette()
            if colors and palette:
                colors.sort(reverse=True, key=lambda x: x[0])
                unique_colors = []
                seen = set()
                for count, index in colors:
                    rgb = (palette[index*3], palette[index*3+1], palette[index*3+2])
                    if rgb not in seen:
                        unique_colors.append(rgb)
                        seen.add(rgb)
                    if len(unique_colors) == 3:
                        break
                color1 = '#%02x%02x%02x' % unique_colors[0] if len(unique_colors) >= 1 else None
                color2 = '#%02x%02x%02x' % unique_colors[1] if len(unique_colors) >= 2 else (color1 if color1 else None)
                color3 = '#%02x%02x%02x' % unique_colors[2] if len(unique_colors) >= 3 else color2
            else:
                color1 = color2 = color3 = None
            # Comprimir la imagen
            if img.format == 'JPEG':
                img.save(self.logo.path, quality=85, optimize=True)
            elif img.format == 'PNG':
                img.save(self.logo.path, optimize=True)
            else:
                img.save(self.logo.path)
            # Actualizar colores en la base de datos
            self.__class__.objects.filter(pk=self.pk).update(color1=color1, color2=color2, color3=color3)

class Categoria(models.Model):
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    max_equipos = models.PositiveIntegerField(default=0)
    tiene_eliminatorias = models.BooleanField(default=False)
    num_equipos_eliminatoria = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.torneo.nombre} - {self.nombre}"

class Equipo(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(
        upload_to='equipos/logos/', 
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
        blank=True, 
        null=True
    )
    color_principal = models.CharField(max_length=7, default='#000000')
    color_secundario = models.CharField(max_length=7, default='#FFFFFF')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    @property
    def capitan(self):
        from .models import Capitan
        try:
            return Capitan.objects.get(equipo=self)
        except Capitan.DoesNotExist:
            return None
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.logo:
            img = Image.open(self.logo.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
            # Comprimir la imagen
            if img.format == 'JPEG':
                img.save(self.logo.path, quality=85, optimize=True)
            elif img.format == 'PNG':
                img.save(self.logo.path, optimize=True)
            else:
                img.save(self.logo.path)

class Jugador(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    foto = models.ImageField(
        upload_to='jugadores/fotos/', 
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
        blank=True, 
        null=True
    )
    fecha_nacimiento = models.DateField()
    numero_camiseta = models.PositiveIntegerField()
    posicion = models.CharField(max_length=50, choices=[
        ('portero', 'Portero'),
        ('defensa', 'Defensa'),
        ('mediocampista', 'Mediocampista'),
        ('delantero', 'Delantero')
    ])
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def save(self, *args, **kwargs):
        # Forzar mayúsculas antes de guardar
        if self.nombre:
            self.nombre = self.nombre.upper()
        if self.apellido:
            self.apellido = self.apellido.upper()
        super().save(*args, **kwargs)
        if self.foto:
            img = Image.open(self.foto.path)
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
            ext = self.foto.path.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg']:
                if img.mode in ('RGBA', 'LA'):
                    img = img.convert('RGB')
                img.save(self.foto.path, format='JPEG', quality=85, optimize=True)
            elif ext == 'png':
                img.save(self.foto.path, format='PNG', optimize=True)
            else:
                img.save(self.foto.path)

class Capitan(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    equipo = models.OneToOneField(Equipo, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.equipo.nombre}"

class Grupo(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.nombre}"

class Partido(models.Model):
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, null=True, blank=True)
    jornada = models.PositiveIntegerField()
    equipo_local = models.ForeignKey(Equipo, related_name='partidos_local', on_delete=models.CASCADE)
    equipo_visitante = models.ForeignKey(Equipo, related_name='partidos_visitante', on_delete=models.CASCADE)
    fecha = models.DateTimeField(null=True, blank=True)
    goles_local = models.PositiveIntegerField(default=0)
    goles_visitante = models.PositiveIntegerField(default=0)
    jugado = models.BooleanField(default=False)
    ubicacion = models.ForeignKey('UbicacionCampo', on_delete=models.SET_NULL, null=True, blank=True, related_name='partidos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - Jornada {self.jornada}"
    
    class Meta:
        ordering = ['jornada', 'fecha']

class Eliminatoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50, choices=[
        ('octavos', 'Octavos de Final'),
        ('cuartos', 'Cuartos de Final'),
        ('semifinal', 'Semifinal'),
        ('tercer_lugar', 'Tercer Lugar'),
        ('final', 'Final')
    ])
    orden = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.categoria.nombre} - {self.get_nombre_display()}"

class PartidoEliminatoria(models.Model):
    eliminatoria = models.ForeignKey(Eliminatoria, on_delete=models.CASCADE)
    equipo_local = models.ForeignKey(Equipo, related_name='partidos_eliminatoria_local', on_delete=models.CASCADE)
    equipo_visitante = models.ForeignKey(Equipo, related_name='partidos_eliminatoria_visitante', on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    goles_local = models.PositiveIntegerField(default=0)
    goles_visitante = models.PositiveIntegerField(default=0)
    goles_local_vuelta = models.PositiveIntegerField(default=0, null=True, blank=True)
    goles_visitante_vuelta = models.PositiveIntegerField(default=0, null=True, blank=True)
    jugado = models.BooleanField(default=False)
    campo = models.CharField(max_length=100, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.eliminatoria.get_nombre_display()}"
    
    class Meta:
        ordering = ['eliminatoria__orden', 'fecha']

class Goleador(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, null=True, blank=True)
    partido_eliminatoria = models.ForeignKey(PartidoEliminatoria, on_delete=models.CASCADE, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    goles = models.PositiveIntegerField(default=1)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.jugador} - {self.goles} goles"
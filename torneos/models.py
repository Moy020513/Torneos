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
    activo = models.BooleanField(default=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

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
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.logo:
            img = Image.open(self.logo.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
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
        super().save(*args, **kwargs)
        if self.foto:
            img = Image.open(self.foto.path)
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
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
    fecha = models.DateTimeField()
    goles_local = models.PositiveIntegerField(default=0)
    goles_visitante = models.PositiveIntegerField(default=0)
    jugado = models.BooleanField(default=False)
    campo = models.CharField(max_length=100, blank=True)
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
from django import template
from datetime import date

register = template.Library()

@register.filter
def punto_decimal(value):
    """Convierte comas en puntos en un string o número"""
    return str(value).replace(',', '.')
from django import template
from datetime import date

register = template.Library()

@register.filter
def punto_decimal(value):
    """Convierte comas en puntos en un string o número"""
    return str(value).replace(',', '.')

@register.filter
def calcular_edad(fecha_nacimiento):
    """Calcula la edad en años basada en la fecha de nacimiento"""
    if not fecha_nacimiento:
        return ''
    
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    
    # Ajustar si aún no ha cumplido años este año
    if hoy.month < fecha_nacimiento.month or (hoy.month == fecha_nacimiento.month and hoy.day < fecha_nacimiento.day):
        edad -= 1
    
    return edad


@register.filter
def times(value):
    """Devuelve un iterable range(0, value) para poder iterar N veces en plantillas."""
    try:
        n = int(value)
        if n < 0:
            return range(0)
        return range(n)
    except Exception:
        return range(0)
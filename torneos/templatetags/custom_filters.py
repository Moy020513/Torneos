from django import template
from datetime import date

register = template.Library()

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
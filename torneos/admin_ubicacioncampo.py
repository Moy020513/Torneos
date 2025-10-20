from django.contrib import admin
from .models import UbicacionCampo

@admin.register(UbicacionCampo)
class UbicacionCampoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'latitud', 'longitud')
    search_fields = ('nombre', 'direccion')

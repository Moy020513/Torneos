from django.urls import path
from . import admin_views

urlpatterns = [
    path('panel/campos/', admin_views.admin_campos, name='admin_campos'),
    path('panel/campos/crear/', admin_views.admin_crear_campo, name='admin_crear_campo'),
    path('panel/campos/<int:campo_id>/editar/', admin_views.admin_editar_campo, name='admin_editar_campo'),
    path('panel/campos/<int:campo_id>/eliminar/', admin_views.admin_eliminar_campo, name='admin_eliminar_campo'),
]

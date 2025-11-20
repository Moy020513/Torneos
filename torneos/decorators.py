from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login

from .models import AdministradorTorneo, Categoria, Equipo


def admin_torneo_required(view_func):
    """Decorador que permite el acceso si el usuario es superuser o
    si es AdministradorTorneo activo para el torneo relacionado con
    los parámetros de la vista (busca `torneo_id`, `categoria_id` o `equipo_id`).
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not getattr(user, 'is_authenticated', False):
            return redirect_to_login(request.get_full_path())

        if getattr(user, 'is_superuser', False):
            return view_func(request, *args, **kwargs)

        # Determinar torneo_id a partir de kwargs
        torneo_id = None
        if 'torneo_id' in kwargs:
            torneo_id = kwargs['torneo_id']
        elif 'categoria_id' in kwargs:
            categoria = get_object_or_404(Categoria, id=kwargs['categoria_id'])
            torneo_id = getattr(categoria.torneo, 'id', None)
        elif 'equipo_id' in kwargs:
            equipo = get_object_or_404(Equipo, id=kwargs['equipo_id'])
            torneo_id = getattr(equipo.categoria.torneo, 'id', None)

        if torneo_id is None:
            return HttpResponseForbidden('Acceso denegado: identificador de torneo no encontrado.')

        has_perm = AdministradorTorneo.objects.filter(usuario=user, activo=True, torneo_id=torneo_id).exists()
        if has_perm:
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden('No tienes permisos para gestionar este torneo.')

    return _wrapped

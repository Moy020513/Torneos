from .models import AdministradorTorneo, Arbitro


def torneo_admin(request):
    """Context processor que agrega información sobre si el usuario es
    administrador de torneo y la instancia asociada.
    Devuelve 'torneo_admin_obj' (o None) y 'is_torneo_admin' boolean.
    """
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'is_torneo_admin': False, 'torneo_admin_obj': None}

    try:
        obj = AdministradorTorneo.objects.select_related('torneo').filter(usuario=request.user, activo=True).first()
    except Exception:
        obj = None

    try:
        arbitro_obj = Arbitro.objects.select_related('torneo').filter(usuario=request.user, activo=True).first()
    except Exception:
        arbitro_obj = None

    return {
        'is_torneo_admin': bool(obj),
        'torneo_admin_obj': obj,
        'is_arbitro': bool(arbitro_obj),
        'arbitro_obj': arbitro_obj,
    }

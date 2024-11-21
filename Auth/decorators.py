from django.http import HttpResponseForbidden
from functools import wraps

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role == role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Vous n'avez pas la permission d'accéder à cette page.")
        return _wrapped_view
    return decorator
# enor_admin/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(roles=['Admin']):
    """
    Decorator to restrict view access by user role.
    Usage:
      @admin_required(roles=['Admin', 'Editor'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('account_login')
            
            try:
                user_role = request.user.profile.role
            except AttributeError:
                messages.error(request, "Profile not found.")
                return redirect('home')
            
            if user_role not in roles:
                messages.warning(request, "You don't have permission to access this page.")
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
"""
Permission decorators for function-based views
"""
from functools import wraps
from django.http import JsonResponse
from .permissions import has_module_access


def require_module_permission(module_code, permission_type='view'):
    """
    Decorator to check module permissions for function-based views
    
    Args:
        module_code (str): The module code to check permissions for
        permission_type (str): The permission type ('view', 'create', 'edit', 'delete')
    
    Usage:
        @require_module_permission('day_end_process', 'delete')
        def delete_day_end_process(request, date):
            # Your function code here
    
    Returns:
        JsonResponse with error if permission denied, otherwise executes the original function
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False, 
                    'message': 'You do not have access to this resource. Authentication required.'
                }, status=403)
            
            # Check if business context is available
            current_zid = getattr(request, 'zid', None)
            if not current_zid:
                return JsonResponse({
                    'success': False, 
                    'message': 'You do not have access to this resource. No business selected.'
                }, status=403)
            
            # Check module permission
            if not has_module_access(request.user, module_code, zid=current_zid, permission_type=permission_type):
                return JsonResponse({
                    'success': False, 
                    'message': f'You do not have access to this resource. {permission_type.title()} permission required for {module_code}.'
                }, status=403)
            
            # Permission granted, execute the original function
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
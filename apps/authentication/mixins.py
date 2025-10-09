from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.shortcuts import redirect
from django.contrib import messages
from .permissions import has_module_access


class ZidRequiredMixin(LoginRequiredMixin):
    """
    Mixin to ensure that a view is only accessible if the user is logged in and has selected a business.
    """
    login_url = '/auth/login/'

    def dispatch(self, request, *args, **kwargs):
        # First check if the user is authenticated
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Then check if ZID is available
        if not hasattr(request, 'zid') or not request.zid:
            messages.error(request, "No business selected. Please log in with a valid Business ID.")
            return redirect('auth-login')

        return super().dispatch(request, *args, **kwargs)


class ModulePermissionMixin(AccessMixin):
    """
    Mixin to enforce module-specific permissions in views.

    Usage:
        class SalesView(ModulePermissionMixin, TemplateView):
            module_code = 'sales'  # Module code to check
            permission_type = 'view'  # Permission type (view, create, edit, delete)
    """
    module_code = None
    permission_type = 'view'

    def dispatch(self, request, *args, **kwargs):
        if not self.module_code:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing module_code attribute."
            )

        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Get current business from session
        current_zid = request.session.get('current_zid')

        if not has_module_access(
            request.user,
            self.module_code,
            zid=current_zid,
            permission_type=self.permission_type
        ):
            raise PermissionDenied("You don't have permission to access this module.")

        return super().dispatch(request, *args, **kwargs)

from django.views.generic import TemplateView
from django.http import HttpResponseForbidden
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper


class PermissionDeniedView(TemplateView):
    """
    Custom 403 Permission Denied view that renders a themed error page
    """
    template_name = "403.html"
    
    def get_context_data(self, **kwargs):
        # Initialize the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        
        # Set the layout for error pages
        context.update({
            "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            "status": 403,
            "error_title": "Access Denied",
            "error_message": "You don't have permission to access this page",
        })
        
        return context
    
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch to return 403 status code"""
        response = super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden(response.rendered_content)


def permission_denied_view(request, exception=None):
    """
    Function-based view for handling 403 errors
    This is the handler that Django will call for 403 errors
    """
    view = PermissionDeniedView.as_view()
    return view(request, exception=exception)
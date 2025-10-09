from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser


class ZidMiddleware(MiddlewareMixin):
    """
    Middleware to ensure the ZID is available in the request for all views
    """
    def process_request(self, request):
        # Only process for authenticated users
        if isinstance(request.user, AnonymousUser):
            return

        # Make sure zid is available in request
        if hasattr(request, 'session') and 'current_zid' in request.session:
            request.zid = request.session['current_zid']
        else:
            request.zid = None

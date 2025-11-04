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


class BusinessInfoMiddleware(MiddlewareMixin):
    """
    Middleware to ensure business information is cached in session and available on request.

    It performs a database lookup ONLY when:
    - current_zid exists, and
    - session has no business_info or it belongs to a different zid.
    """
    def process_request(self, request):
        # Only process for authenticated users
        if isinstance(request.user, AnonymousUser):
            return

        # Determine current ZID
        zid = getattr(request, 'zid', None)
        if not zid and hasattr(request, 'session'):
            zid = request.session.get('current_zid')
        if not zid or not hasattr(request, 'session'):
            return

        # If business_info already matches current zid, attach and return
        info = request.session.get('business_info')
        if isinstance(info, dict) and info.get('zid') == zid:
            request.business_info = info
            return

        # Otherwise, fetch from DB once and cache in session
        try:
            from apps.authentication.models import Business
            business = Business.objects.filter(zid=zid).first()
            if business:
                info = {
                    'zid': business.zid,
                    'business_name': business.name or '',
                    'business_address': business.address or '',
                    'business_mobile': business.mobile or '',
                    'business_email': business.email or '',
                    'business_website': business.website or '',
                }
                request.session['business_info'] = info
                request.business_info = info
        except Exception:
            # Silently ignore lookup failures; templates will fallback gracefully
            pass

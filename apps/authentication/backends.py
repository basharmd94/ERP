from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Business, UserBusinessAccess


class ZidAuthenticationBackend(ModelBackend):
    """
    Custom authentication backend that checks ZID, username, and password
    """
    def authenticate(self, request, username=None, password=None, zid=None, **kwargs):
        if not all([username, password, zid]):
            return None

        try:
            # First, check if the business with given ZID exists
            business = Business.objects.get(zid=zid, is_active=True)

            # Then try to authenticate the user with username and password
            user = super().authenticate(request, username=username, password=password)

            if user:
                # Check if user has access to this business
                if UserBusinessAccess.objects.filter(user=user, business=business).exists():
                    # Store the selected business in the session
                    if request and hasattr(request, 'session'):
                        request.session['current_zid'] = zid
                        request.session['current_business'] = business.name
                    return user
        except Business.DoesNotExist:
            pass

        return None

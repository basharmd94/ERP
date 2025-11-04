def current_business(request):
    """
    Context processor to add current business information to all templates.

    Provides:
    - current_zid: Active business ZID from session
    - current_business: Legacy name string if present in session
    - business: Dict with detailed business info (name, address, contact, website)
    """
    context = {
        'current_zid': None,
        'current_business': None,
        'business': {},
    }

    if request.user.is_authenticated and hasattr(request, 'session'):
        context['current_zid'] = request.session.get('current_zid')
        context['current_business'] = request.session.get('current_business')

        # Prefer request.business_info if middleware populated it; fallback to session
        business_info = getattr(request, 'business_info', None) or request.session.get('business_info')
        if isinstance(business_info, dict):
            context['business'] = business_info

        # Attach request to user object for permission checks
        request.user.request = request

    return context

def current_business(request):
    """
    Context processor to add current ZID and business name to all templates
    """
    context = {
        'current_zid': None,
        'current_business': None,
    }

    if request.user.is_authenticated and hasattr(request, 'session'):
        context['current_zid'] = request.session.get('current_zid')
        context['current_business'] = request.session.get('current_business')
        # Attach request to user object for permission checks
        request.user.request = request

    return context

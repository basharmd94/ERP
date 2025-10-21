from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
@require_http_methods(["GET"])
def get_current_zid_api(request):
    """
    API endpoint to get current ZID from session for JavaScript
    """
    try:
        # Debug logging
        logger.info(f"Session keys: {list(request.session.keys())}")
        logger.info(f"Session data: {dict(request.session)}")

        current_zid = request.session.get('current_zid')
        logger.info(f"Retrieved current_zid: {current_zid}")

        if not current_zid:
            logger.warning("No current_zid found in session")
            return JsonResponse({
                'success': False,
                'message': 'No business context found',
                'debug_info': {
                    'session_keys': list(request.session.keys()),
                    'user_authenticated': request.user.is_authenticated,
                    'username': request.user.username if request.user.is_authenticated else None
                }
            }, status=400)

        response = JsonResponse({
            'success': True,
            'zid': current_zid
        })

        # Add cache control headers to prevent caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response

    except Exception as e:
        logger.error(f"Error getting current ZID: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to get business context',
            'error': str(e)
        }, status=500)

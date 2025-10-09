from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin
from ..models.caitem import Caitem
import logging

logger = logging.getLogger(__name__)


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class ItemsView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'crossapp_items'
    template_name = 'items.html'
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


@login_required
def get_items_json(request):
    """Get items list with specific columns as JSON"""
    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        logger.info(f"get_items_json called by user: {request.user.username}, current_zid: {current_zid}")
        if not current_zid:
            logger.warning(f"No business context found for user: {request.user.username}")
            return JsonResponse({'error': 'No business context found'}, status=400)

        # Get search parameter from Select2
        search_term = request.GET.get('search', '').strip()
        logger.info(f"Search term: '{search_term}', ZID: {current_zid}")

        # Query items for the current ZID with specific fields
        items_query = Caitem.objects.filter(zid=current_zid)
        logger.info(f"Initial query count for ZID {current_zid}: {items_query.count()}")
        
        # Apply search filter if search term is provided
        if search_term:
            from django.db.models import Q
            items_query = items_query.filter(
                Q(xitem__icontains=search_term) | 
                Q(xdesc__icontains=search_term)
            )
        
        # Limit results for performance (Select2 pagination)
        page = int(request.GET.get('page', 1))
        page_size = 20
        start = (page - 1) * page_size
        end = start + page_size
        
        items = items_query.values(
            'xitem',      # Item Code
            'xdesc',      # Description
            'xgitem',     # Item Group
            'xwh',        # Warehouse
            'xstdcost',   # Standard Cost
            'xstdprice',  # Standard Price
            'xunitstk'    # Stock Unit
        )[start:end]

        # Convert Decimal fields to string for JSON serialization
        items_list = list(items)
        for item in items_list:
            if item['xstdcost']:
                item['xstdcost'] = str(item['xstdcost'])
            if item['xstdprice']:
                item['xstdprice'] = str(item['xstdprice'])

        # Get total count for pagination
        total_count = items_query.count()
        has_more = end < total_count
        
        logger.info(f"Returning {len(items_list)} items out of {total_count} total for ZID {current_zid}")

        return JsonResponse({
            'items': items_list,
            'pagination': {
                'more': has_more
            },
            'total_count': total_count
        }, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delete_item_api(request, item_code):
    """Delete an existing item"""
    
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for item deletion by user: {request.user.username}")
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')

        try:
            queryset = Caitem.objects.filter(zid=current_zid, xitem=item_code)
            item = queryset.first()
            if not item:
                logger.warning(f"Item not found for deletion: {item_code} for business: {current_zid}")
                return JsonResponse({'error': 'Item not found'}, status=404)
            logger.debug(f"Found item to delete: zid={item.zid}, xitem={item.xitem}")
        except Caitem.DoesNotExist:
            logger.warning(f"Item not found for deletion: {item_code} for business: {current_zid}")
            return JsonResponse({'error': 'Item not found'}, status=404)
        
        item_name = item.xdesc or item.xitem
        logger.debug(f"Deleting item {item_name} (code: {item_code}) for business: {current_zid} by user: {request.user.username}")
        
        # Use a specific delete query to ensure only one record is deleted
        deleted_count = Caitem.objects.filter(
            zid=current_zid,
            xitem=item_code
        ).delete()
        
        logger.info(f"Item deleted successfully: {item_name} (code: {item_code}) for business: {current_zid} by user: {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Item deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)} for user: {request.user.username}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
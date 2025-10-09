from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin
from ..models.xcodes import Xcodes
import json
import logging

logger = logging.getLogger(__name__)


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class ItemGroupView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'crossapp_item_group'
    template_name = 'item_group.html'
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # Add module code to context
        return context


def get_item_group_json(request):
    """Get item group list with specific columns as JSON"""
    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            return JsonResponse({'error': 'No business context found'}, status=400)

        # Query item group for the current ZID with specific fields
# Query item group for the current ZID with specific fields and xtype = 'Brand'
        item_group = Xcodes.objects.filter(
            zid=current_zid,
            xtype='Item Group'  # Only include records where xtype is 'Brand'
        ).values(
            'xcode',      # Item Group Code
            'xdescdet',   # Item Group Description
            'zactive',    # Item Group Status
        )
        # Convert Decimal fields to string for JSON serialization
        item_group_list = list(item_group)
        logger.info(f"Retrieved item group for ZID {current_zid}: {item_group_list}")
        return JsonResponse({'item_group': item_group_list}, safe=False)
    except Exception as e:
        logger.error(f"Error retrieving item group: {str(e)}")
        return JsonResponse({'error': str(e)}, status=404)


# create a new item group as like brand
@login_required
def create_item_group_api(request):
    """Create a new item group"""
    logger.info(f"Item group creation attempt by user: {request.user.username}")

    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for item group creation by user: {request.user.username}")
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            logger.warning(f"No business context found for item group creation by user: {request.user.username}")
            return JsonResponse({'status': 'error', 'message': 'No business context found'}, status=400)

        logger.debug(f"Creating item group for ZID: {current_zid}")

        # Get item group name from POST data
        data = json.loads(request.body)
        item_group_name = data.get('item_group_description', '').strip()
        if not item_group_name:
            logger.warning(f"Empty item group name provided by user: {request.user.username}")
            return JsonResponse({'status': 'error', 'message': 'Item group name is required'}, status=400)

        logger.debug(f"Attempting to create item group: {item_group_name}")

        # Check if item group already exists (exact match)
        existing_item_group = Xcodes.objects.filter(
            zid=current_zid,
            xtype='Item Group',
            xcode=item_group_name
        ).first()

        if existing_item_group:
            logger.warning(f"Duplicate item group creation attempt: {item_group_name} already exists for business: {current_zid}")
            return JsonResponse({'status': 'error', 'message': 'Item group already exists'}, status=400)

        # Create new item group
        item_group = Xcodes.objects.create(
            xcode=item_group_name,
            xdescdet=item_group_name,
            zid=current_zid,
            xtype='Item Group',
            zactive='1'
        )
        return JsonResponse({
            'status': 'success',
            'message': 'Item group created successfully',
            'item_group': {
                'item_group_code': item_group.xcode,
                'item_group_name': item_group.xdescdet
            }
        })
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error creating item group: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# ✅ NO ELSE BLOCK HERE — it was causing the bug!@login_required
def update_item_group_api(request, item_group_code):
    """Update an existing item group"""
    logger.info(f"Item group update attempt by user: {request.user.username} for item group: {item_group_code}")

    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for item group update by user: {request.user.username}")
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            logger.warning(f"No business context found for item group update by user: {request.user.username}")
            return JsonResponse({'status': 'error', 'message': 'No business context found'}, status=400)

        logger.debug(f"Updating item group {item_group_code} for ZID: {current_zid}")

        # Get the item group to update
        try:
            item_group = Xcodes.objects.get(
                zid=current_zid,
                xtype='Item Group',
                xcode=item_group_code
            )
        except Xcodes.DoesNotExist:
            logger.warning(f"Item group not found: {item_group_code} for business: {current_zid}")
            return JsonResponse({'status': 'error', 'message': 'Item group not found'}, status=404)

        # Get new item group name from request data
        data = json.loads(request.body)  # ← Now this will work!
        new_item_group_name = data.get('item_group_description', '').strip()
        if not new_item_group_name:
            logger.warning(f"Empty item group name provided for update by user: {request.user.username}")
            return JsonResponse({'status': 'error', 'message': 'Item group name is required'}, status=400)

        logger.debug(f"Updating item group {item_group_code} to: {new_item_group_name}")

        # Check if new item group name already exists (excluding current item group)
        if new_item_group_name != item_group_code:
            existing_item_group = Xcodes.objects.filter(
                zid=current_zid,
                xtype='Item Group',
                xcode=new_item_group_name
            ).exclude(xcode=item_group_code).first()

            if existing_item_group:
                logger.warning(f"Duplicate item group name during update: {new_item_group_name} already exists for business: {current_zid}")
                return JsonResponse({'status': 'error', 'message': 'Item group name already exists'}, status=400)

        # Update item group using filter and update
        Xcodes.objects.filter(
            zid=current_zid,
            xtype='Item Group',
            xcode=item_group_code
        ).update(
            xcode=new_item_group_name,
            xdescdet=new_item_group_name
        )

        logger.info(f"Item group updated successfully: {item_group_code} -> {new_item_group_name}")
        return JsonResponse({
            'status': 'success',
            'message': 'Item group updated successfully',
            'item_group': {
                'item_group_code': new_item_group_name,
                'item_group_name': new_item_group_name
            }
        })

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({
            'status': 'error',
            'message': 'Request body must be valid JSON. Example: {"item_group_description": "Electronics"}'
        }, status=400)
    except Exception as e:
        logger.error(f"Error updating item group: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# ✅ NO ELSE BLOCK HERE — it was causing silent overrides!
@login_required
def delete_item_group_api(request, item_group_code):
    """Delete an existing item group"""
    logger.info(f"Item group deletion attempt by user: {request.user.username} for item group: {repr(item_group_code)}")

    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for item group deletion by user: {request.user.username}")
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'}, status=405)

    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            logger.warning(f"No business context found for item group deletion by user: {request.user.username}")
            return JsonResponse({'status': 'error', 'message': 'No business context found'}, status=400)



        logger.debug(f"Attempting to delete item group with xcode='{item_group_code}' for ZID={current_zid}")

        # Delete matching record(s) — SAFELY using filter + delete()
        deleted_count, _ = Xcodes.objects.filter(
            zid=current_zid,
            xcode=item_group_code,      # Exact match (already lowercased)
            xtype='Item Group'          # Hardcoded type
        ).delete()

        if deleted_count == 0:
            logger.warning(f"Item group not found for deletion: {item_group_code} for business: {current_zid}")
            return JsonResponse({'status': 'error', 'message': 'Item group not found'}, status=404)

        logger.info(f"Successfully deleted {deleted_count} item group(s): {item_group_code} by user: {request.user.username}")
        return JsonResponse({
            'status': 'success',
            'message': 'Item group deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting item group: {str(e)} for user: {request.user.username}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=500)

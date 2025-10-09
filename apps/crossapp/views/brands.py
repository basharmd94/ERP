import logging
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from web_project import TemplateLayout
from apps.authentication.mixins import ZidRequiredMixin
from apps.authentication.mixins import ModulePermissionMixin
from ..models.xcodes import Xcodes

# Get logger for this module
logger = logging.getLogger(__name__)


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class BrandsView(ZidRequiredMixin, ModulePermissionMixin, TemplateView):
    module_code = 'crossapp_items_brand'
    template_name = 'brands.html'
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


@login_required
def get_brands_json(request):
    """Get brands list with specific columns as JSON"""
    logger.info(f"Getting brands list for user: {request.user.username}")

    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            logger.warning(f"No business context found for user: {request.user.username}")
            return JsonResponse({'error': 'No business context found'}, status=400)

        logger.debug(f"Current ZID: {current_zid}")

        # Query brands for the current ZID with specific fields
        brands = Xcodes.objects.filter(zid=current_zid, xtype='Brand').values(
            'xcode',
            'xdescdet',
            'zactive',
        )

        # Convert brands data to list for JSON serialization
        brands_list = list(brands)
        logger.info(f"Successfully retrieved {len(brands_list)} brands for business: {current_zid}")
        return JsonResponse({'brands': brands_list}, safe=False)

    except Exception as e:
        logger.error(f"Error retrieving brands: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def create_brand_api(request):
    """Create a new brand"""
    logger.info(f"Brand creation attempt by user: {request.user.username}")

    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for brand creation by user: {request.user.username}")
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            logger.warning(f"No business context found for brand creation by user: {request.user.username}")
            return JsonResponse({'error': 'No business context found'}, status=400)

        logger.debug(f"Creating brand for ZID: {current_zid}")

        # Get Business instance

        # Get brand name from POST data
        brand_name = request.POST.get('brandName', '').strip()
        if not brand_name:
            logger.warning(f"Empty brand name provided by user: {request.user.username}")
            return JsonResponse({'error': 'Brand name is required'}, status=400)

        logger.debug(f"Attempting to create brand: {brand_name}")

        # Check if brand already exists (exact match)
        existing_brand = Xcodes.objects.filter(
            zid=current_zid,
            xtype='Brand',
            xcode=brand_name
        ).first()

        if existing_brand:
            logger.warning(f"Duplicate brand creation attempt: {brand_name} already exists for business: {current_zid}")
            return JsonResponse({'error': 'Brand already exists'}, status=400)

        # Create new brand
        new_brand = Xcodes.objects.create(
            xcode=brand_name,
            xdescdet=brand_name,
            zid=current_zid,
            xtype='Brand',
            zactive = '1'
        )

        logger.info(f"Brand created successfully: {brand_name} (code: {brand_name}) for business: {current_zid} by user: {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': 'Brand created successfully',
            'brand': {
                'xcode': new_brand.xcode,
                'xdescdet': new_brand.xdescdet
            }
        })

    except Exception as e:
        logger.error(f"Error creating brand: {str(e)} for user: {request.user.username}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def update_brand_api(request, brand_code):
    """Update an existing brand"""
    logger.info(f"Brand update attempt by user: {request.user.username} for brand: {brand_code}")

    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for brand update by user: {request.user.username}")
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')
        if not current_zid:
            logger.warning(f"No business context found for brand update by user: {request.user.username}")
            return JsonResponse({'error': 'No business context found'}, status=400)

        logger.debug(f"Updating brand {brand_code} for ZID: {current_zid}")

        # Get Business instance

        # Get the brand to update
        try:
            brand = Xcodes.objects.get(
                zid=current_zid,
                xtype='Brand',
                xcode=brand_code
            )
        except Xcodes.DoesNotExist:
            logger.warning(f"Brand not found: {brand_code} for business: {current_zid}")
            return JsonResponse({'error': 'Brand not found'}, status=404)

        # Get new brand name from POST data
        new_brand_name = request.POST.get('brandName', '').strip()
        if not new_brand_name:
            logger.warning(f"Empty brand name provided for update by user: {request.user.username}")
            return JsonResponse({'error': 'Brand name is required'}, status=400)

        logger.debug(f"Updating brand {brand_code} to: {new_brand_name}")

        # Check if new brand name already exists (excluding current brand)
        logger.debug(f"Original brand code: {brand_code}")
        logger.debug(f"New brand code: {new_brand_name}")

        if new_brand_name != brand_code:
            existing_brand_query = Xcodes.objects.filter(
                zid=current_zid,
                xtype='Brand',
                xcode=new_brand_name
            ).exclude(xcode=brand_code)

            logger.debug(f"Existing brand check query: {existing_brand_query.query}")
            existing_brand = existing_brand_query.first()

            if existing_brand:
                logger.warning(f"Duplicate brand name during update: {new_brand_name} already exists for business: {current_zid}")
                return JsonResponse({'error': 'Brand name already exists'}, status=400)

        # Update brand using filter and update to avoid primary key issues with managed=False
        Xcodes.objects.filter(
            zid=current_zid,
            xtype='Brand',
            xcode=brand_code  # Filter by the original xcode
        ).update(
            xcode=new_brand_name,
            xdescdet=new_brand_name
        )

        logger.info(f"Brand updated successfully: {brand_code} -> {new_brand_name} (code: {new_brand_name}) for business: {current_zid} by user: {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': 'Brand updated successfully',
            'brand': {
                'xcode': brand.xcode,
                'xdescdet': brand.xdescdet
            }
        })

    except Exception as e:
        logger.error(f"Error updating brand: {str(e)} for user: {request.user.username}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def delete_brand_api(request, brand_code):
    """Delete an existing brand"""

    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for brand deletion by user: {request.user.username}")
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    try:
        # Get current ZID from session
        current_zid = request.session.get('current_zid')

        try:
            queryset = Xcodes.objects.filter(zid=current_zid, xtype='Brand', xcode=brand_code)
            brand = queryset.first()
            if not brand:
                logger.warning(f"Brand not found for deletion: {brand_code} for business: {current_zid}")
                return JsonResponse({'error': 'Brand not found'}, status=404)
            logger.debug(f"Found brand to delete: zid={brand.zid}, xtype={brand.xtype}, xcode={brand.xcode}")
        except Xcodes.DoesNotExist:
            logger.warning(f"Brand not found for deletion: {brand_code} for business: {current_zid}")
            return JsonResponse({'error': 'Brand not found'}, status=404)

        brand_name = brand.xcode
        logger.debug(f"Deleting brand {brand_name} (code: {brand_code}) for business: {current_zid} by user: {request.user.username}")

        # Use a more specific delete query to ensure only one record is deleted
        deleted_count = Xcodes.objects.filter(
            zid=current_zid,
            xtype='Brand',
            xcode=brand_code
        ).delete()

        logger.info(f"Brand deleted successfully: {brand_name} (code: {brand_code}) for business: {current_zid} by user: {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': 'Brand deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting brand: {str(e)} for user: {request.user.username}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

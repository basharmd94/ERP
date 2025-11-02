from django import template
from apps.authentication.permissions import has_module_permission, has_module_access

register = template.Library()

@register.filter
def has_menu_permission(user, permission_code):
    """
    Template filter to check if user has permission for a menu item
    Usage: {% if user|has_menu_permission:menu_item.permission %}
    """
    if not permission_code:
        return True

    if not hasattr(user, 'request'):
        print(f"DEBUG: No request on user object for permission {permission_code}")
        return False

    current_zid = getattr(user.request, 'zid', None)
    if not current_zid:
        print(f"DEBUG: No ZID in request for permission {permission_code}")
        return False

    has_perm = has_module_permission(user, current_zid, permission_code)
    print(f"DEBUG: Checking permission {permission_code} for user {user.username} with ZID {current_zid}: {has_perm}")
    return has_perm

@register.filter
def has_submenu_permissions(user, submenu):
    """
    Check if user has permission to see any items in submenu
    Usage: {% if user|has_submenu_permissions:menu_item.submenu %}
    """
    if not submenu:
        print("DEBUG: No submenu provided")
        return False

    if not hasattr(user, 'request'):
        print("DEBUG: No request on user for submenu check")
        return False

    # Check if user has permission for at least one submenu item
    for item in submenu:
        permission_code = item.get('permission')
        if not permission_code:
            print("DEBUG: No permission required for submenu item", item)
            return True

        current_zid = getattr(user.request, 'zid', None)
        if current_zid and has_module_permission(user, current_zid, permission_code):
            print(f"DEBUG: Found permitted submenu item {item} for user {user.username}")
            return True
        else:
            print(f"DEBUG: No permission for submenu item {item} for user {user.username}")

    print("DEBUG: No permitted submenu items found")
    return False

@register.filter
def has_module_access_permission(user, permission_string):
    """
    Template filter to check if user has specific module access permission
    Usage: {% if user|has_module_access_permission:"day_end_process:create" %}
    """
    if not permission_string:
        return False

    try:
        module_code, permission_type = permission_string.split(':')
    except ValueError:
        print(f"DEBUG: Invalid permission string format: {permission_string}")
        return False

    if not hasattr(user, 'request'):
        print(f"DEBUG: No request on user object for permission {permission_string}")
        return False

    current_zid = getattr(user.request, 'zid', None)
    if not current_zid:
        print(f"DEBUG: No ZID in request for permission {permission_string}")
        return False

    has_perm = has_module_access(user, module_code, zid=current_zid, permission_type=permission_type)
    print(f"DEBUG: Checking module access {permission_string} for user {user.username} with ZID {current_zid}: {has_perm}")
    return has_perm

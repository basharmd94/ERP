"""
Utility functions for checking module permissions
"""
from .models import Business, Module, UserBusinessAccess, UserGroupMembership, BusinessModuleGroupAccess


def has_business_access(user, zid=None, business=None):
    """
    Check if a user has access to a business

    Args:
        user: The user to check
        zid: The ZID of the business (optional if business is provided)
        business: The business object (optional if zid is provided)

    Returns:
        bool: True if the user has access, False otherwise
    """
    if user.is_superuser:
        return True

    if not zid and not business:
        return False

    if zid and not business:
        try:
            business = Business.objects.get(zid=zid)
        except Business.DoesNotExist:
            return False

    # Check if user has direct access to the business
    return UserBusinessAccess.objects.filter(user=user, business=business).exists()


def has_module_access(user, module_code, zid=None, business=None, permission_type='view'):
    """
    Check if a user has access to a specific module in a business

    Args:
        user: The user to check
        module_code: The code of the module
        zid: The ZID of the business (optional if business is provided)
        business: The business object (optional if zid is provided)
        permission_type: The type of permission to check (view, create, edit, delete)

    Returns:
        bool: True if the user has access, False otherwise
    """
    print(f"DEBUG: Checking module access for {user.username} - module: {module_code}, zid: {zid}, type: {permission_type}")

    if user.is_superuser:
        print("DEBUG: User is superuser")
        return True

    if not zid and not business:
        print("DEBUG: No ZID or business provided")
        return False

    if zid and not business:
        try:
            business = Business.objects.get(zid=zid)
            print(f"DEBUG: Found business {business.name} for ZID {zid}")
        except Business.DoesNotExist:
            print(f"DEBUG: No business found for ZID {zid}")
            return False

    # First check if user has direct access to the business
    if not UserBusinessAccess.objects.filter(user=user, business=business).exists():
        print(f"DEBUG: User {user.username} does not have business access to {business}")
        return False

    try:
        module = Module.objects.get(code=module_code)
        print(f"DEBUG: Found module {module.name} for code {module_code}")
    except Module.DoesNotExist:
        print(f"DEBUG: Module not found for code {module_code}")
        return False

    # Get all permission groups the user belongs to
    user_group_objects = UserGroupMembership.objects.filter(user=user).select_related('group')
    user_group_names = [membership.group.name for membership in user_group_objects]
    print(f"DEBUG: User {user.username} belongs to groups: {user_group_names}")

    # Check if any of the user's groups have the required permission for this module in this business
    permission_field = f'can_{permission_type}'

    # Get all BusinessModuleGroupAccess records for this business and module
    access_records = BusinessModuleGroupAccess.objects.filter(
        business=business,
        module=module,
        **{permission_field: True}
    )

    print(f"DEBUG: Found {access_records.count()} access records for {module.name} in {business.name}")

    # Check if any of the access records contain groups that the user belongs to
    has_permission = False
    for record in access_records:
        record_groups = record.get_group_list()
        print(f"DEBUG: Access record groups: {record_groups}")

        # Check if any of the user's groups are in this record's group list
        if any(group_name in record_groups for group_name in user_group_names):
            has_permission = True
            print(f"DEBUG: Found matching group in record: {record.groups}")
            break

    print(f"DEBUG: Permission check result for {permission_type}: {has_permission}")
    return has_permission


def has_module_permission(user, zid, permission_code):
    """
    Check if a user has permission to access a specific module/feature

    Args:
        user: The user to check permissions for
        zid: The business ZID context
        permission_code: The permission code to check (e.g. 'crossapp.view')

    Returns:
        bool: True if the user has permission, False otherwise
    """
    print(f"DEBUG: Checking module permission for user {user.username} (superuser: {user.is_superuser})")

    if user.is_superuser:
        print(f"DEBUG: User {user.username} is superuser, granting permission")
        return True

    if not permission_code:
        return True

    if not has_business_access(user, zid=zid):
        return False

    # Split the permission code into module and action
    try:
        module_name, action = permission_code.split('.')
    except ValueError:
        return False

    # Check module access with the specific permission type
    return has_module_access(user, module_name, zid=zid, permission_type=action)

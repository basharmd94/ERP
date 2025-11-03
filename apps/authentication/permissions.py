"""
Utility functions for checking module permissions
"""
from .models import Business, Module, UserBusinessAccess, UserGroupMembership, BusinessModuleAccess, PermissionGroup


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
    Check if a user has access to a specific module in a business using the new permission group system

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
    user_groups = [membership.group for membership in user_group_objects]
    user_group_names = [group.name for group in user_groups]
    print(f"DEBUG: User {user.username} belongs to groups: {user_group_names}")

    # Get the BusinessModuleAccess record for this business and module
    try:
        module_access = BusinessModuleAccess.objects.get(
            business=business,
            module=module,
            is_active=True
        )
        print(f"DEBUG: Found module access record for {module.name} in {business.name}")
    except BusinessModuleAccess.DoesNotExist:
        print(f"DEBUG: No module access record found for {module.name} in {business.name}")
        return False

    # Get the list of permission groups assigned to this module
    assigned_groups = module_access.get_permission_groups_list()
    print(f"DEBUG: Module {module.name} has assigned groups: {assigned_groups}")

    # Check if any of the user's groups are in the assigned groups and have the required permission
    has_permission = False
    for user_group in user_groups:
        if user_group.name in assigned_groups:
            print(f"DEBUG: User group {user_group.name} is assigned to module {module.name}")
            # Check if this group has the required permission type
            if user_group.has_permission(permission_type):
                has_permission = True
                print(f"DEBUG: Group {user_group.name} has {permission_type} permission")
                break
            else:
                print(f"DEBUG: Group {user_group.name} does not have {permission_type} permission (has: {user_group.permissions})")

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


def get_user_module_permissions(user, zid):
    """
    Get all module permissions for a user in a specific business

    Args:
        user: The user to get permissions for
        zid: The business ZID context

    Returns:
        dict: Dictionary with module codes as keys and permission types as values
    """
    if user.is_superuser:
        return {}  # Superuser has all permissions

    try:
        business = Business.objects.get(zid=zid)
    except Business.DoesNotExist:
        return {}

    if not UserBusinessAccess.objects.filter(user=user, business=business).exists():
        return {}

    # Get user's groups
    user_groups = UserGroupMembership.objects.filter(user=user).select_related('group')
    user_group_names = [membership.group.name for membership in user_groups]
    user_group_dict = {group.group.name: group.group for group in user_groups}

    # Get all module access records for this business
    module_access_records = BusinessModuleAccess.objects.filter(
        business=business,
        is_active=True
    ).select_related('module')

    permissions = {}
    for record in module_access_records:
        assigned_groups = record.get_permission_groups_list()
        module_permissions = []

        for group_name in assigned_groups:
            if group_name in user_group_names:
                group = user_group_dict[group_name]
                if group.permissions == 'full':
                    module_permissions.extend(['view', 'create', 'edit', 'delete'])
                else:
                    module_permissions.append(group.permissions)

        if module_permissions:
            permissions[record.module.code] = list(set(module_permissions))  # Remove duplicates

    return permissions

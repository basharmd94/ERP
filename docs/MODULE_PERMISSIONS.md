# Module Permissions System Documentation

## Overview
The ERP system uses a hierarchical permission system based on:
1. Businesses (identified by ZID)
2. Modules (features/sections of the application)
3. Permission Groups
4. User Group Memberships
5. Business Module Group Access

## Components

### 1. Business
- Represents a business unit with a unique ZID
- Users must have access to a business before they can access any modules
```python
# Example of Business model usage
business = Business.objects.create(
    zid='1000',
    name='Sample Business',
    is_active=True
)
```

### 2. Modules
- Represents features or sections of the application
- Each module has a unique code and can belong to a group
```python
# Example of Module creation
module = Module.objects.create(
    name='Items List',
    code='crossapp_items_list',
    description='Access to view item list',
    group='Cross App',
    is_active=True
)
```

### 3. Permission Groups
- Groups that define sets of permissions
- Users are assigned to these groups
```python
# Example of Permission Group creation
permission_group = PermissionGroup.objects.create(
    name='Sales Team',
    description='Sales team members',
    is_active=True
)
```

### 4. User Group Membership
- Links users to permission groups
```python
# Example of assigning user to a group
UserGroupMembership.objects.create(
    user=user,
    group=permission_group
)
```

### 5. Business Module Group Access
- Defines which permission groups have access to which modules in which businesses
```python
# Example of granting module access to a group
BusinessModuleGroupAccess.objects.create(
    business=business,
    module=module,
    group=permission_group,
    can_view=True,
    can_create=True,
    can_edit=True,
    can_delete=False
)
```

## Step-by-Step Example: Setting Up Module Permissions

### 1. Creating a New Module in Django Admin

1. Navigate to Django Admin > Modules > Add
2. Fill in the details:
```
Name: Items List
Code: crossapp_items_list
Description: Access to view item list
Group: Cross App
Is active: ✓
```

### 2. Creating a Permission Group

1. Navigate to Django Admin > Permission Groups > Add
2. Fill in the details:
```
Name: Sales Team
Description: Sales team with items view access
Is active: ✓
```

### 3. Assigning Users to the Group

1. Navigate to Django Admin > User Group Memberships > Add
2. Select:
```
User: [Select User]
Group: Sales Team
```

### 4. Granting Module Access

1. Navigate to Django Admin > Business Module Group Access > Add
2. Configure:
```
Business: [Select Business/ZID]
Module: Items List
Group: Sales Team
Can view: ✓
Can create: ✗
Can edit: ✗
Can delete: ✗
```

### 5. Implementing in Views

```python
from apps.authentication.mixins import ModulePermissionMixin
from django.views.generic import TemplateView

class ItemsListView(ModulePermissionMixin, TemplateView):
    module_code = 'crossapp_items_list'
    template_name = 'items_list.html'
```

### 6. Configuring Menu Items

In `vertical_menu.json`:
```json
{
  "name": "Items",
  "icon": "menu-icon tf-icons ti ti-box",
  "slug": "crossapp-items",
  "permission": "crossapp_items.view",
  "submenu": [
    {
      "url": "crossapp-items",
      "name": "Item List",
      "slug": "crossapp-items-list",
      "permission": "crossapp_items_list.view"
    }
  ]
}
```

## Best Practices

1. **Module Codes**
   - Use lowercase letters and underscores
   - Include the app name as prefix (e.g., `crossapp_items_list`)
   - Make them descriptive and unique

2. **Permission Granularity**
   - Create separate modules for distinct features
   - Don't reuse module codes across different features
   - Use specific permissions rather than general ones

3. **Group Management**
   - Create groups based on roles rather than individuals
   - Use descriptive group names
   - Document group purposes and permissions

4. **Testing Permissions**
```python
# Example of checking permissions in code
from apps.authentication.permissions import has_module_permission

if has_module_permission(user, zid='1000', permission_code='crossapp_items_list.view'):
    # User has access to view items list
    pass
```

## Troubleshooting

### Common Issues

1. **User can't access any modules**
   - Check if user has business access (UserBusinessAccess)
   - Verify user is assigned to a permission group
   - Ensure the business is active

2. **User sees unauthorized modules**
   - Check menu configuration permissions
   - Verify BusinessModuleGroupAccess settings
   - Check module codes match exactly

3. **Permission not taking effect**
   - Clear browser cache
   - Verify module code spelling
   - Check debug logs in permissions.py

### Debug Tips

Enable debug logging in settings:
```python
# settings.py
LOGGING = {
    'handlers': {
        'console': {
            'level': 'DEBUG',
        },
    },
}
```

Monitor permission checks in console:
```
DEBUG: Checking module access for user1 - module: crossapp_items_list, zid: 1000, type: view
DEBUG: User user1 belongs to groups: [1, 2]
DEBUG: Permission check result for view: True
```

## Security Considerations

1. Always use ModulePermissionMixin for views
2. Don't bypass permission checks
3. Regularly audit permission assignments
4. Keep modules and permissions granular
5. Document all custom permission requirements

# Quick Start Guide: Setting Up Module Permissions

This guide demonstrates setting up permissions for a new feature using a real-world example.

## Scenario
Adding a new "Customer Reports" feature that should only be accessible to sales managers.

## Step 1: Create the Module

In Django Admin > Modules > Add:
```
Name: Customer Reports
Code: sales_customer_reports
Description: Access to customer sales reports
Group: Sales
Is active: ✓
```

## Step 2: Create Permission Group

In Django Admin > Permission Groups > Add:
```
Name: Sales Managers
Description: Sales team leaders with reporting access
Is active: ✓
```

## Step 3: Set Up Business Access

In Django Admin > Business Module Group Access > Add:
```
Business: [Your ZID]
Module: Customer Reports
Group: Sales Managers
Can view: ✓
Can create: ✓
Can edit: ✗
Can delete: ✗
```

## Step 4: Add the View

```python
# views.py
from apps.authentication.mixins import ModulePermissionMixin
from django.views.generic import TemplateView

class CustomerReportsView(ModulePermissionMixin, TemplateView):
    module_code = 'sales_customer_reports'
    template_name = 'sales/customer_reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your report data here
        return context
```

## Step 5: Add URL Pattern

```python
# urls.py
from django.urls import path
from .views import CustomerReportsView

urlpatterns = [
    path('customer-reports/', CustomerReportsView.as_view(), name='customer-reports'),
]
```

## Step 6: Add Menu Item

In `vertical_menu.json`:
```json
{
  "name": "Sales",
  "submenu": [
    {
      "url": "customer-reports",
      "name": "Customer Reports",
      "slug": "sales-customer-reports",
      "permission": "sales_customer_reports.view"
    }
  ]
}
```

## Step 7: Assign Users

In Django Admin > User Group Memberships > Add:
```
User: [Select Sales Manager]
Group: Sales Managers
```

## Verification

1. Log in as a sales manager
2. Verify you can see the "Customer Reports" menu item
3. Verify you can access the reports page
4. Log in as a regular user
5. Verify the menu item is not visible

## Troubleshooting

If access is not working:

1. Check console logs for permission debugging info
2. Verify module code matches exactly in all places
3. Confirm user has business access
4. Confirm user is in the correct group
5. Verify BusinessModuleGroupAccess entry exists

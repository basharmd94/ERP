# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Business(models.Model):
    """Business model to represent different business units with unique ZIDs"""
    zid = models.IntegerField(unique=True, primary_key=True, verbose_name="Business ID",)
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    mobile = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.zid})"


class Module(models.Model):
    """Model to represent different modules in the ERP system"""
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    group = models.CharField(max_length=150, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PermissionGroup(models.Model):
    """Model to define permission groups with specific CRUD permissions"""
    PERMISSION_CHOICES = [
        ('view', 'View'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.TextField(
        blank=True,
        help_text="Comma-separated list of permissions (view, create, edit, delete)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        permissions_display = self.get_permissions_list()
        if permissions_display:
            return f"{self.name} ({', '.join(permissions_display)})"
        return f"{self.name} (No permissions)"

    def get_permissions_list(self):
        """Get list of permissions for this group"""
        if not self.permissions:
            return []
        return [perm.strip() for perm in self.permissions.split(',') if perm.strip()]

    def set_permissions_list(self, permissions_list):
        """Set permissions from a list"""
        self.permissions = ','.join(permissions_list)

    def has_permission(self, permission_type):
        """Check if this group has a specific permission"""
        return permission_type in self.get_permissions_list()

    def add_permission(self, permission_type):
        """Add a permission to this group"""
        permissions = self.get_permissions_list()
        if permission_type not in permissions:
            permissions.append(permission_type)
            self.set_permissions_list(permissions)

    def remove_permission(self, permission_type):
        """Remove a permission from this group"""
        permissions = self.get_permissions_list()
        if permission_type in permissions:
            permissions.remove(permission_type)
            self.set_permissions_list(permissions)

    class Meta:
        verbose_name = 'Permission Group'
        verbose_name_plural = 'Permission Groups'


class UserGroupMembership(models.Model):
    """Model to assign users to permission groups"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE, related_name='members')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')
        verbose_name = 'User Group Membership'
        verbose_name_plural = 'User Group Memberships'

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"


class BusinessModuleAccess(models.Model):
    """Model to manage comma-separated permission groups for modules within businesses"""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='module_access')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    permission_groups = models.TextField(
        help_text="Comma-separated permission group names (e.g., 'group-a,group-b,group-c')"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business', 'module')
        verbose_name = 'Business Module Access'
        verbose_name_plural = 'Business Module Access'

    def __str__(self):
        return f"{self.module.name} - {self.business.name} ({self.permission_groups})"

    def get_permission_groups_list(self):
        """Return list of permission group names"""
        if not self.permission_groups:
            return []
        return [group.strip() for group in self.permission_groups.split(',') if group.strip()]

    def has_group_access(self, group_name):
        """Check if a specific group has access to this module"""
        return group_name in self.get_permission_groups_list()

    def add_permission_group(self, group_name):
        """Add a permission group to this module access"""
        groups = self.get_permission_groups_list()
        if group_name not in groups:
            groups.append(group_name)
            self.permission_groups = ','.join(groups)
            self.save()

    def remove_permission_group(self, group_name):
        """Remove a permission group from this module access"""
        groups = self.get_permission_groups_list()
        if group_name in groups:
            groups.remove(group_name)
            self.permission_groups = ','.join(groups)
            self.save()


class UserBusinessAccess(models.Model):
    """Model to handle user access to different businesses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_access')
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'business')
        verbose_name_plural = 'User Business Access'

    def __str__(self):
        return f"{self.user.username} - {self.business.name}"

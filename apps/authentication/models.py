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
    """Model to define permission groups for module access"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UserGroupMembership(models.Model):
    """Model to assign users to permission groups"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE, related_name='members')

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"


class BusinessModuleGroupAccess(models.Model):
    """Model to manage group access to specific modules within businesses"""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='module_permissions')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    groups = models.TextField(
        help_text="Comma-separated list of group names (e.g., 'Sales,Purchase,SOP')"
    )
    can_view = models.BooleanField(default=True)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('business', 'module')
        verbose_name_plural = 'Business Module Group Access'

    def __str__(self):
        return f"{self.groups} - {self.module.name} - {self.business.name}"

    def get_group_list(self):
        """Return a list of group names from the comma-separated string"""
        if not self.groups:
            return []
        return [group.strip() for group in self.groups.split(',') if group.strip()]

    def has_group(self, group_name):
        """Check if a specific group is in the comma-separated list"""
        return group_name in self.get_group_list()

    def add_group(self, group_name):
        """Add a group to the comma-separated list if not already present"""
        groups = self.get_group_list()
        if group_name not in groups:
            groups.append(group_name)
            self.groups = ','.join(groups)

    def remove_group(self, group_name):
        """Remove a group from the comma-separated list"""
        groups = self.get_group_list()
        if group_name in groups:
            groups.remove(group_name)
            self.groups = ','.join(groups)


class UserBusinessAccess(models.Model):
    """Model to handle user access to different businesses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_access')
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'business')
        verbose_name_plural = 'User Business Access'

    def __str__(self):
        return f"{self.user.username} - {self.business.name}"

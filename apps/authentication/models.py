# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Business(models.Model):
    """Business model to represent different business units with unique ZIDs"""
    zid = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
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
    group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE)
    can_view = models.BooleanField(default=True)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('business', 'module', 'group')
        verbose_name_plural = 'Business Module Group Access'

    def __str__(self):
        return f"{self.group.name} - {self.module.name} - {self.business.name}"


class UserBusinessAccess(models.Model):
    """Model to handle user access to different businesses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_access')
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'business')
        verbose_name_plural = 'User Business Access'

    def __str__(self):
        return f"{self.user.username} - {self.business.name}"

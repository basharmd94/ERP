# Register your models here.
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Business, UserBusinessAccess, Module, PermissionGroup, UserGroupMembership, BusinessModuleAccess


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('zid', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('zid', 'name')
    ordering = ('zid',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'group')
    list_filter = ('is_active', 'group')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)


class PermissionGroupForm(forms.ModelForm):
    """Custom form for PermissionGroup with checkbox widgets for permissions"""
    VIEW_PERMISSION = 'view'
    CREATE_PERMISSION = 'create'
    EDIT_PERMISSION = 'edit'
    DELETE_PERMISSION = 'delete'

    view_permission = forms.BooleanField(label='View', required=False)
    create_permission = forms.BooleanField(label='Create', required=False)
    edit_permission = forms.BooleanField(label='Edit', required=False)
    delete_permission = forms.BooleanField(label='Delete', required=False)

    class Meta:
        model = PermissionGroup
        fields = ('name', 'description', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If we're editing an existing instance, set the checkboxes based on permissions
        if self.instance.pk:
            permissions = self.instance.get_permissions_list()
            self.fields['view_permission'].initial = self.VIEW_PERMISSION in permissions
            self.fields['create_permission'].initial = self.CREATE_PERMISSION in permissions
            self.fields['edit_permission'].initial = self.EDIT_PERMISSION in permissions
            self.fields['delete_permission'].initial = self.DELETE_PERMISSION in permissions

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Build permissions list from checkboxes
        permissions = []
        if self.cleaned_data.get('view_permission'):
            permissions.append(self.VIEW_PERMISSION)
        if self.cleaned_data.get('create_permission'):
            permissions.append(self.CREATE_PERMISSION)
        if self.cleaned_data.get('edit_permission'):
            permissions.append(self.EDIT_PERMISSION)
        if self.cleaned_data.get('delete_permission'):
            permissions.append(self.DELETE_PERMISSION)

        # Set permissions as comma-separated string
        instance.set_permissions_list(permissions)

        if commit:
            instance.save()
        return instance


@admin.register(PermissionGroup)
class PermissionGroupAdmin(admin.ModelAdmin):
    form = PermissionGroupForm
    list_display = ('name', 'permissions_display', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    def permissions_display(self, obj):
        """Display permissions in a readable format"""
        permissions = obj.get_permissions_list()
        if not permissions:
            return "No permissions"
        return ", ".join(permissions)
    permissions_display.short_description = "Permissions"

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Permissions', {
            'fields': ('view_permission', 'create_permission', 'edit_permission', 'delete_permission'),
            'description': 'Select the permissions for this group'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserGroupMembership)
class UserGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'assigned_at')
    list_filter = ('group', 'assigned_at')
    search_fields = ('user__username', 'group__name')
    autocomplete_fields = ('user', 'group')
    readonly_fields = ('assigned_at',)


@admin.register(BusinessModuleAccess)
class BusinessModuleAccessAdmin(admin.ModelAdmin):
    list_display = ('business', 'module', 'permission_groups_display', 'is_active', 'created_at')
    list_filter = ('business', 'module', 'is_active', 'created_at')
    search_fields = ('business__name', 'module__name', 'permission_groups')
    autocomplete_fields = ('business', 'module')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('business', 'module', 'permission_groups', 'is_active')
        }),
        ('Help', {
            'fields': (),
            'description': 'Enter comma-separated permission group names. Example: group-a,group-b,group-c'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def permission_groups_display(self, obj):
        """Display permission groups in a more readable format"""
        groups = obj.get_permission_groups_list()
        if not groups:
            return "No groups assigned"
        return ", ".join(groups)
    permission_groups_display.short_description = "Permission Groups"

    def get_form(self, request, obj=None, **kwargs):
        """Customize the form to add help text"""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['permission_groups'].help_text = (
            "Enter comma-separated permission group names.<br>"
            "Example: <strong>group-a,group-b,group-c</strong><br>"
            "Each group should exist in the Permission Groups section."
        )
        return form


@admin.register(UserBusinessAccess)
class UserBusinessAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'business')
    list_filter = ('business',)
    search_fields = ('user__username', 'business__name', 'business__zid')
    autocomplete_fields = ('user', 'business')


# Add information about business access to the User admin
class UserBusinessAccessInline(admin.TabularInline):
    model = UserBusinessAccess
    extra = 1
    verbose_name = "Business Access"
    verbose_name_plural = "Business Access"


# Add information about group membership to the User admin
class UserGroupMembershipInline(admin.TabularInline):
    model = UserGroupMembership
    extra = 1
    verbose_name = "Group Membership"
    verbose_name_plural = "Group Memberships"
    readonly_fields = ('assigned_at',)


# Extend the UserAdmin to include business access and group membership
class CustomUserAdmin(UserAdmin):
    inlines = list(UserAdmin.inlines) + [UserBusinessAccessInline, UserGroupMembershipInline]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

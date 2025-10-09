# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Business, UserBusinessAccess, Module, PermissionGroup, UserGroupMembership, BusinessModuleGroupAccess


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('zid', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('zid', 'name')
    ordering = ('zid',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'group')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)


@admin.register(PermissionGroup)
class PermissionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(UserGroupMembership)
class UserGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group')
    list_filter = ('group',)
    search_fields = ('user__username', 'group__name')
    autocomplete_fields = ('user', 'group')


@admin.register(BusinessModuleGroupAccess)
class BusinessModuleGroupAccessAdmin(admin.ModelAdmin):
    list_display = ('business', 'module', 'group', 'can_view', 'can_create', 'can_edit', 'can_delete')
    list_filter = ('business', 'module', 'group', 'can_view', 'can_create', 'can_edit', 'can_delete')
    search_fields = ('business__name', 'module__name', 'group__name')
    autocomplete_fields = ('business', 'module', 'group')


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


# Extend the UserAdmin to include business access and group membership
class CustomUserAdmin(UserAdmin):
    inlines = list(UserAdmin.inlines) + [UserBusinessAccessInline, UserGroupMembershipInline]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

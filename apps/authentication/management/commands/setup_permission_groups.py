"""
Management command to set up sample permission groups for testing the new authorization system
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.authentication.models import (
    Business, Module, PermissionGroup, UserGroupMembership,
    BusinessModuleAccess, UserBusinessAccess
)


class Command(BaseCommand):
    help = 'Set up sample permission groups and test data for the new authorization system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all permission groups and module access data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting permission groups and module access...')
            BusinessModuleAccess.objects.all().delete()
            UserGroupMembership.objects.all().delete()
            PermissionGroup.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Reset completed.'))

        # Create sample permission groups
        self.stdout.write('Creating sample permission groups...')

        groups_data = [
            {
                'name': 'viewers',
                'permissions': 'view',
                'description': 'Users who can only view data'
            },
            {
                'name': 'editors',
                'permissions': 'edit',
                'description': 'Users who can view and edit data'
            },
            {
                'name': 'creators',
                'permissions': 'create',
                'description': 'Users who can view and create new data'
            },
            {
                'name': 'deletors',
                'permissions': 'delete',
                'description': 'Users who can delete data'
            },
            {
                'name': 'admins',
                'permissions': 'full',
                'description': 'Users with full access (all permissions)'
            },
            {
                'name': 'accountants',
                'permissions': 'edit',
                'description': 'Accounting staff with edit permissions'
            },
            {
                'name': 'managers',
                'permissions': 'full',
                'description': 'Department managers with full access'
            }
        ]

        created_groups = []
        for group_data in groups_data:
            group, created = PermissionGroup.objects.get_or_create(
                name=group_data['name'],
                defaults={
                    'permissions': group_data['permissions'],
                    'description': group_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_groups.append(group.name)
                self.stdout.write(f'  Created group: {group.name} ({group.get_permissions_display()})')
            else:
                self.stdout.write(f'  Group already exists: {group.name}')

        # Get or create sample business
        business, created = Business.objects.get_or_create(
            zid=1001,
            defaults={
                'name': 'Sample Business Corp',
                'address': '123 Business Street',
                'city': 'Business City',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created sample business: {business.name}')

        # Get or create sample modules
        modules_data = [
            {'name': 'Chart of Accounts', 'code': 'chart_of_accounts', 'group': 'Accounting'},
            {'name': 'Voucher Entry', 'code': 'voucher_entry', 'group': 'Accounting'},
            {'name': 'Day End Process', 'code': 'day_end_process', 'group': 'Accounting'},
            {'name': 'Year End Processing', 'code': 'year_end_processing', 'group': 'Accounting'},
            {'name': 'Cheque Management', 'code': 'cheque_management', 'group': 'Banking'},
            {'name': 'Bank Reconciliation', 'code': 'bank_reconciliation', 'group': 'Banking'},
        ]

        created_modules = []
        for module_data in modules_data:
            module, created = Module.objects.get_or_create(
                code=module_data['code'],
                defaults={
                    'name': module_data['name'],
                    'group': module_data['group'],
                    'is_active': True
                }
            )
            if created:
                created_modules.append(module.code)
                self.stdout.write(f'  Created module: {module.name} ({module.code})')

        # Create sample module access assignments
        self.stdout.write('Creating sample module access assignments...')

        access_assignments = [
            # Module A - viewers(view), editors(edit)
            {
                'module_code': 'chart_of_accounts',
                'groups': 'viewers,editors,accountants'
            },
            # Module B - creators(create), deletors(delete)
            {
                'module_code': 'voucher_entry',
                'groups': 'creators,deletors,accountants,managers'
            },
            {
                'module_code': 'day_end_process',
                'groups': 'managers,admins'
            },
            {
                'module_code': 'year_end_processing',
                'groups': 'admins'
            },
            {
                'module_code': 'cheque_management',
                'groups': 'editors,accountants,managers'
            },
            {
                'module_code': 'bank_reconciliation',
                'groups': 'accountants,managers,admins'
            }
        ]

        for assignment in access_assignments:
            try:
                module = Module.objects.get(code=assignment['module_code'])
                access, created = BusinessModuleAccess.objects.get_or_create(
                    business=business,
                    module=module,
                    defaults={
                        'permission_groups': assignment['groups'],
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'  Assigned groups "{assignment["groups"]}" to module {module.name}')
                else:
                    # Update existing assignment
                    access.permission_groups = assignment['groups']
                    access.save()
                    self.stdout.write(f'  Updated groups for module {module.name}')
            except Module.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Module {assignment["module_code"]} not found'))

        # Create sample user assignments (if users exist)
        self.stdout.write('Assigning sample users to groups...')

        # Try to find existing users or create sample ones
        sample_users = [
            {'username': 'john_viewer', 'groups': ['viewers']},
            {'username': 'jane_editor', 'groups': ['editors', 'accountants']},
            {'username': 'bob_manager', 'groups': ['managers']},
            {'username': 'alice_admin', 'groups': ['admins']},
        ]

        for user_data in sample_users:
            try:
                user = User.objects.get(username=user_data['username'])

                # Ensure user has business access
                UserBusinessAccess.objects.get_or_create(
                    user=user,
                    business=business
                )

                # Assign user to groups
                for group_name in user_data['groups']:
                    try:
                        group = PermissionGroup.objects.get(name=group_name)
                        membership, created = UserGroupMembership.objects.get_or_create(
                            user=user,
                            group=group
                        )
                        if created:
                            self.stdout.write(f'  Assigned user {user.username} to group {group.name}')
                    except PermissionGroup.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'  Group {group_name} not found'))

            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  User {user_data["username"]} not found'))

        self.stdout.write(self.style.SUCCESS('\nSetup completed successfully!'))
        self.stdout.write('\nSample configuration:')
        self.stdout.write('- Chart of Accounts: viewers, editors, accountants')
        self.stdout.write('- Voucher Entry: creators, deletors, accountants, managers')
        self.stdout.write('- Day End Process: managers, admins')
        self.stdout.write('- Year End Processing: admins only')
        self.stdout.write('- Cheque Management: editors, accountants, managers')
        self.stdout.write('- Bank Reconciliation: accountants, managers, admins')
        self.stdout.write('\nYou can now test the permission system in the Django admin!')
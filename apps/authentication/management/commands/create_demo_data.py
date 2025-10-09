from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.authentication.models import Business, UserBusinessAccess


class Command(BaseCommand):
    help = 'Creates demo business data for ERP system'

    def handle(self, *args, **options):
        # Create businesses
        businesses = [
            {'zid': '100001', 'name': 'Fixit'},
            {'zid': '100002', 'name': 'Central'},
            {'zid': '100003', 'name': 'Ecommerce'},
            {'zid': '100004', 'name': 'Green Road'},
        ]

        for biz in businesses:
            business, created = Business.objects.get_or_create(
                zid=biz['zid'],
                defaults={'name': biz['name']}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created business: {business.name} (ZID: {business.zid})"))
            else:
                self.stdout.write(f"Business already exists: {business.name} (ZID: {business.zid})")

        # Create a demo superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_user.username}"))

            # Give admin access to all businesses
            for business in Business.objects.all():
                UserBusinessAccess.objects.get_or_create(user=admin_user, business=business)

            self.stdout.write(self.style.SUCCESS("Gave admin access to all businesses"))
        else:
            admin_user = User.objects.get(username='admin')
            self.stdout.write("Admin user already exists")

        # Create demo users
        demo_users = [
            {'username': 'user1', 'password': 'user1', 'zids': ['100001', '100002']},
            {'username': 'user2', 'password': 'user2', 'zids': ['100003']},
            {'username': 'user3', 'password': 'user3', 'zids': ['100001', '100004']},
        ]

        for user_data in demo_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={'is_staff': False, 'is_superuser': False}
            )

            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))
            else:
                self.stdout.write(f"User already exists: {user.username}")

            # Assign business access
            for zid in user_data['zids']:
                try:
                    business = Business.objects.get(zid=zid)
                    access, created = UserBusinessAccess.objects.get_or_create(user=user, business=business)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Gave {user.username} access to {business.name}"))
                except Business.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Business with ZID {zid} does not exist"))

        self.stdout.write(self.style.SUCCESS("Demo data creation completed"))

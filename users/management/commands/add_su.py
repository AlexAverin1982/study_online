from django.core.management import BaseCommand
from django.conf import settings

from users.models import CustomUser

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        user = CustomUser.objects.create(email=settings.ADMIN_MAIL)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.set_password(settings.ADMIN_DEFAULT_PASSWORD)
        user.save()

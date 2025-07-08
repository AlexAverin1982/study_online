from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Добавление в базу данных групп контроля доступа к данным сервиса"

    def handle(self, *args, **kwargs) -> None:
        Group.objects.all().delete()

        managers = Group.objects.create(name='Moderators')
        # block_user = Permission.objects.get(codename='can_block_user')
        # disable_mailing = Permission.objects.get(codename='can_disable_mailing')

        # managers.permissions.add(block_user, disable_mailing)
        group = Group.objects.get(name='Moderators')

        if group:
            self.stdout.write(
                self.style.SUCCESS(f"успешно добавлена группа: {group.name}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Такая группа уже существует: {group.name}")
            )

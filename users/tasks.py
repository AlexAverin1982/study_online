import datetime as dt
from celery import shared_task
from users.models import CustomUser


@shared_task
def check_inactive_users():
    now = dt.datetime.now(dt.timezone.utc)
    for user in CustomUser.objects.all():
        if user.is_active and ((now - user.last_login).total_seconds() > 3600 * 24 * 30):
            user.is_active = False
            user.save()

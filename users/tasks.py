import datetime as dt
from celery import shared_task
from django.shortcuts import get_object_or_404
from users.models import CustomUser

@shared_task
def check_inactive_users(pk, model):
    print('*'*100)
    user = get_object_or_404(CustomUser, id=pk)
    now = dt.datetime.now(dt.timezone.utc)
    if (now - user.last_login).total_seconds() > 3600 * 24 * 20:
        user.is_active = False
        user.save()

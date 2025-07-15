"""
функционал администратора сервиса
"""
from datetime import datetime as dt
from django_celery_beat.models import PeriodicTask, IntervalSchedule

def enable_periodic_task(*args, **kwargs):
    name = kwargs.get('name')
    if not name:
        return
    if PeriodicTask.objects.filter(name=name).exists():
        task = PeriodicTask.objects.filter(name=name)[0]
        task.enabled = True
        task.save()
    else:
        every = kwargs.get('every')
        period = str(kwargs.get('period')).lower()
        if period == 'hours':
            period = IntervalSchedule.HOURS
        elif period == 'days':
            period = IntervalSchedule.DAYS
        elif period == 'minutes':
            period = IntervalSchedule.MINUTES
        elif period == 'seconds':
            period = IntervalSchedule.SECONDS

        if every and period:
            schedule, created = IntervalSchedule.objects.get_or_create(every=every, period=period)

            task = kwargs.get('task')
            expires = kwargs.get('expires')

            if task and expires:
                PeriodicTask.objects.create(
                    interval=schedule,
                    name=name,
                    task=task,
                    start_time=dt.now(),
                    expires=expires
                )

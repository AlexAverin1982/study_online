from celery import shared_task
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings

from materials.models import Subscription, Course


@shared_task
def notify_users_of_course_updated(course_id: int):
    course = get_object_or_404(Course, id=course_id)
    subs = Subscription.objects.filter(course=course)
    subscribers = [s.user for s in subs]
    subscribers = [u.email for u in subscribers]

    # print('*' * 100)
    # for s in subscribers:
    #     print(f"subscriber: {s}")

    topic = f"Курс {course.name} обновился."
    text = f"Курс {course.name} обновился."
    send_mail(topic, text, settings.EMAIL_HOST_USER, subscribers, fail_silently=False)
    # return subscribers

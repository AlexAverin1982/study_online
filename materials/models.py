from django.db import models

# from users.models import CustomUser


class Course(models.Model):
    """
    Модель обучающего курса
    """
    name = models.CharField(max_length=100, verbose_name="Название")
    preview = models.ImageField(upload_to='static/course_preview/', blank=True, null=True, verbose_name="Превью")
    description = models.TextField(max_length=2000, verbose_name="Описание", blank=True)
    owner = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, related_name='courses',
                              verbose_name='Владелец', blank=True, null=True)
    product = models.CharField(max_length=100, verbose_name="Идентификатор stripe", blank=True)
    price = models.IntegerField(default=0, verbose_name='Цена курса в рублях')
    stripe_price = models.CharField(max_length=100, verbose_name="Идентификатор цены stripe", blank=True)
    # url_to_buy = models.URLField(verbose_name='Ссылка на покупку курса', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Обучающий курс"
        verbose_name_plural = "курсы"
        ordering = ["name"]
        # permissions = [('can_block_user', 'Can block and unblock users'), ]


class Lesson(models.Model):
    """
    Модель урока
    """
    name = models.CharField(max_length=100, verbose_name="Название урока")
    preview = models.ImageField(upload_to='static/lesson_preview/', blank=True, null=True, verbose_name="Превью")
    description = models.TextField(max_length=2000, verbose_name="Описание урока", blank=True)
    seq_number = models.IntegerField(default=0, verbose_name='Порядковый номер урока в курсе')
    video = models.URLField(blank=True, default='', verbose_name="Ссылка на видео на youtube.com")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, related_name='Уроки',
                               verbose_name='Курс', blank=True, null=True)
    owner = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, related_name='lessons',
                              verbose_name='Владелец', blank=True, null=True)

    price = models.IntegerField(default=0, verbose_name='Цена урока в рублях')
    stripe_price = models.CharField(max_length=100, verbose_name="Идентификатор цены stripe", blank=True)
    # url_to_buy = models.URLField(verbose_name='Ссылка на покупку урока', blank=True)

    def __str__(self):
        return f"{self.seq_number}. {self.name}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "уроки"
        ordering = ["name"]
        # permissions = [('can_block_user', 'Can block and unblock users'), ]


class Subscription(models.Model):
    """
    Модель подписки на обновление курса для пользователя
    """
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='subscriptions',
                             verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions',
                               verbose_name='Курс')

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "подписки"
        ordering = ["course", "user"]

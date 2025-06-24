from django.db import models


class Course(models.Model):
    """
    Модель обучающего курса
    """
    name = models.CharField(max_length=100, verbose_name="Название")
    preview = models.ImageField(upload_to='static/course_preview/', blank=True, null=True, verbose_name="Превью")
    description = models.TextField(max_length=2000, verbose_name="Описание", blank=True)

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
    name = models.CharField(max_length=100, verbose_name="Название")
    preview = models.ImageField(upload_to='static/lesson_preview/', blank=True, null=True, verbose_name="Превью")
    description = models.TextField(max_length=2000, verbose_name="Описание", blank=True)
    seq_number = models.IntegerField(default=0)
    video = models.FileField(upload_to='lesson_videos', blank=True, null=True, verbose_name="Видео")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, related_name='Уроки',
                               verbose_name='Курс', blank=True, null=True)

    def __str__(self):
        return f"{self.seq_number}. {self.name}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "уроки"
        ordering = ["name"]
        # permissions = [('can_block_user', 'Can block and unblock users'), ]

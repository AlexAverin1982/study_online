from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from rest_framework.generics import get_object_or_404
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='static/avatars/', blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    courses_bought = models.ManyToManyField('materials.Course', verbose_name='Купленные курсы')
    lessons_bought = models.ManyToManyField('materials.Lesson', verbose_name='Купленные уроки')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "пользователи"
        ordering = ["last_name", "first_name"]
        # permissions = [('can_block_user', 'Can block and unblock users'), ]


class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='Платежи',
                             verbose_name='Платеж', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")
    course = models.ForeignKey('materials.Course', on_delete=models.SET_NULL, related_name='Платежи',
                               verbose_name='Оплаченный курс', blank=True, null=True)

    lesson = models.ForeignKey('materials.Lesson', on_delete=models.SET_NULL, related_name='Платежи',
                               verbose_name='Оплаченный урок', blank=True, null=True)

    cash = models.BooleanField(default=False, verbose_name='Оплачено наличными')

    sum = models.FloatField(blank=False, verbose_name='Сумма', validators=[MinValueValidator(100.0)])

    session = models.CharField(verbose_name='Идентификатор сессии покупки', blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        from materials.models import Lesson
        if self.lesson:
            print(f"self.lesson: {self.lesson.id}")
            lesson_obj = Lesson.objects.get(id=self.lesson.id)
            # lesson_obj = get_object_or_404(Lesson, id=self.lesson)
            print("-" * 100)
            print(f"lesson_obj.course: {lesson_obj.course}")

            if self.course:
                if lesson_obj.course != self.course:
                    raise ValidationError('Курс оплаченного урока указан неверно')
            else:

                if lesson_obj.course:


                    self.course = lesson_obj.course
                else:
                    raise ValidationError('Курс оплаченного урока не указан')
        else:
            if not self.course:
                raise ValidationError("Необходимо указать либо оплачиваемый курс, либо курс и входящий в него урок.")

        if self.sum <= 0.0:
            raise ValidationError("Сумма платежа не указана или указана неверно.")

    # overriden to make sure the clean() method is called whenever object is to be created
    def save(self, *args, **kwargs):
        self.clean()
        self.full_clean()  # here, complete validation is performed
        super().save(*args, **kwargs)  # then model does the rest

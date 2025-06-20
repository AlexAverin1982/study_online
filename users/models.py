from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from materials.models import Course, Lesson


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='static/avatars/', blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "пользователи"
        ordering = ["last_name", "first_name"]
        # permissions = [('can_block_user', 'Can block and unblock users'), ]


class UsersControl(models.Model):
    users = models.ManyToManyField(CustomUser, verbose_name="Пользователи, которым можно заходить в приложение")

    class Meta:
        verbose_name = "Управление пользователями"


class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='Платежи',
                             verbose_name='Платеж', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")

    course = models.ForeignKey(Course, on_delete=models.SET_NULL, related_name='Платежи',
                               verbose_name='Оплаченный курс', blank=True, null=True)

    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, related_name='Платежи',
                               verbose_name='Оплаченный урок', blank=True, null=True)

    cash = models.BooleanField(default=False, verbose_name='Оплачено наличными')

    sum = models.FloatField(blank=False, verbose_name='Сумма', validators=[MinValueValidator(100.0)])

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.lesson:
            if self.course:
                lesson_obj = Lesson.objects.get(id=self.lesson)
                if lesson_obj.course != self.course:
                    raise ValidationError('Курс оплаченного урока указан неверно')
            else:
                raise ValidationError('Курс оплаченного урока не указан')
        else:
            if not self.course:
                raise ValidationError("Необходимо указать либо оплачиваемый курс, либо курс и входящий в него урок.")

        if self.sum <= 0.0:
            raise ValidationError("Сумма платежа не указана или указана неверно.")

    # overriden to make sure the clean() method is called whenever object is to be created
    def save(self, *args, **kwargs):
        self.full_clean()  # here, complete validation is performed
        super().save(*args, **kwargs)  # then model does the rest

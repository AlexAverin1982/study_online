from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from .mixins import FormControlMixin
from .models import CustomUser, UsersControl


class LoginForm(FormControlMixin, forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class CustomUserCreationForm(FormControlMixin, UserCreationForm):
    # phone_number = forms.CharField(max_length=15, required=False,
    #                                help_text='Необязательное поле. Введите ваш номер телефона.')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'email', 'username', 'first_name', 'last_name',
            'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
    #
    # def clean_phone_number(self):
    #     phone_number = self.cleaned_data.get('phone_number')
    #     if phone_number and not phone_number.isdigit():
    #         raise forms.ValidationError('Номер телефона должен содержать только цифры')
    #     return phone_number
    #


class CustomUserUpdateForm(FormControlMixin, UserChangeForm):
    # phone_number = forms.CharField(max_length=15, required=False,
    #                                help_text='Необязательное поле. Введите ваш номер телефона.')

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = (
            'email', 'username', 'first_name', 'last_name', 'phone_number', 'avatar', 'city', 'is_superuser')

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)

    # def clean_phone_number(self):
    #     phone_number = self.cleaned_data.get('phone_number')
    #     if phone_number and not phone_number.isdigit():
    #         raise forms.ValidationError('Номер телефона должен содержать только цифры')
    #     return phone_number


class UsersControlForm(FormControlMixin, forms.ModelForm):
    users = forms.ModelMultipleChoiceField(queryset=CustomUser.objects.all())

    class Meta:
        model = UsersControl
        fields = '__all__'  # no use, form is customized, but without it server won't start


class UsersControlInitForm(FormControlMixin, forms.ModelForm):
    users = forms.ModelMultipleChoiceField(queryset=CustomUser.objects.all(),
                                           label="Пользователи, которым можно заходить в приложение")

    class Meta:
        model = UsersControl
        fields = '__all__'  # no use, form is customized, but without it server won't start


class UserForgotPasswordForm(PasswordResetForm):
    """
    Запрос на восстановление пароля
    """

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })


class UserSetNewPasswordForm(SetPasswordForm):
    """
    Изменение пароля пользователя после подтверждения
    """

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

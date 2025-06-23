from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.views.generic import DeleteView, UpdateView, TemplateView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.models import Site
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from typing_extensions import Any
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserSetNewPasswordForm
from .forms import CustomUserCreationForm, CustomUserUpdateForm, UsersControlInitForm
from .mixins import UserIsNotAuthenticated
from .models import CustomUser, UsersControl, Payment
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from .serializers import CustomUserSerializer, PaymentSerializer, PaymentCreateSerializer

User = get_user_model()


class UserLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'
    next_page = 'home'

    def get(self, request, **kwargs):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request, **kwargs):
        AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('materials:home'))
        else:
            messages.error(request, 'Логин или пароль неправильные')
            return redirect(reverse('materials:home'))


class RegisterView(UserIsNotAuthenticated, CreateView):
    """
     Представление регистрации на сайте с формой регистрации
     """
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/user_register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация на сайте'
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        # Функционал для отправки письма и генерации токена
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_url = reverse_lazy('confirm_email', kwargs={'uidb64': uid, 'token': token})
        current_site = Site.objects.get_current().domain
        send_mail(
            'Подтвердите свой электронный адрес для регистрации на сайте study_online',
            f'Пожалуйста, перейдите по следующей ссылке, '
            f'чтобы подтвердить свой адрес электронной почты: http://{current_site}{activation_url}',
            settings.ADMIN_MAIL,
            [user.email],
            fail_silently=False,
        )
        return redirect('email_confirmation_sent')


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserDeleteView(DeleteView):
    model = CustomUser
    success_url = reverse_lazy("home")
    template_name = 'delete_user.html'


class CustomUserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class CustomUserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class UserUpdateView(UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = 'register.html'

    extra_context = {
        'User_editing_mode': True,
    }


    def get_success_url(self):
        return reverse("user_profile", kwargs=self.kwargs)


class UserConfirmEmailView(View):

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('email_confirmed')
        else:
            return redirect('email_confirmation_failed')


class EmailConfirmationSentView(TemplateView):
    template_name = 'email_confirmation_sent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Письмо активации отправлено'
        return context


class EmailConfirmedView(TemplateView):
    template_name = 'email_confirmed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш электронный адрес активирован'
        return context


class EmailConfirmationFailedView(TemplateView):
    template_name = 'email_confirmation_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ваш электронный адрес не активирован'
        return context


class UsersControlView(UpdateView):
    model = UsersControl
    form_class = UsersControlInitForm
    template_name = "init_users_control.html"
    context_object_name = 'control'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'users': CustomUser.objects.all(),
        })

        return context

    def post(self, request, *args, **kwargs) -> Any:
        req_data = dict(request.POST.copy())
        data_in_form = UsersControlInitForm(request.POST)
        active_users = sorted([int(id) for id in req_data['users']])
        print(f"active_users: {active_users}")

        all_users = CustomUser.objects.all().values_list('id', flat=True)
        inactive_users = all_users.exclude(id__in=active_users)

        if data_in_form.is_valid():
            if inactive_users:
                for id in inactive_users:
                    user = get_object_or_404(CustomUser, pk=id)
                    user.is_active = False
                    user.save()
            else:
                inactive_users = CustomUser.objects.filter(is_active=False)
                inactive_users.update(is_active=True)
                for user in inactive_users:
                    user.save()
            return HttpResponseRedirect(reverse_lazy('home'))
        else:
            return HttpResponseRedirect(reverse('errors'))


class InitUsersControlView(CreateView):
    model = UsersControl
    form_class = UsersControlInitForm
    template_name = 'init_users_control.html'
    context_object_name = 'control'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'users': CustomUser.objects.all(),
        })

        return context

    def post(self, request, *args, **kwargs) -> Any:
        data = UsersControlInitForm(request.POST)

        print(f"request.POST: {request.POST}")
        print(f"users: {request.POST.get('users')}")

        if data.is_valid():
            update = data.save(commit=False)
            update.owner = request.user
            update.save()
            data.save_m2m()
            return HttpResponseRedirect(reverse_lazy('home'))
        else:
            return HttpResponseRedirect(reverse('errors'))


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """
    Представление по сбросу пароля по почте
    """
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """
    Представление установки нового пароля
    """
    form_class = UserSetNewPasswordForm
    template_name = 'user_password_set_new.html'
    success_url = reverse_lazy('home')
    success_message = 'Пароль успешно изменен. Можете авторизоваться на сайте.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Установить новый пароль'
        return context


class CreatePaymentAPIView(generics.CreateAPIView):
    queryset = Payment.objects.all
    serializer_class = PaymentCreateSerializer


class DeletePaymentAPIView(generics.DestroyAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()


class PaymentsListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('course', 'lesson', 'cash', 'user', 'created_at')
    ordering_fields = ['course', 'lesson', 'cash', 'user', 'created_at', 'user']

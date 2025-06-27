from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.models import Site
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from typing_extensions import Any
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserSetNewPasswordForm
from .forms import CustomUserCreationForm, UsersControlInitForm
from .mixins import UserIsNotAuthenticated
from .models import CustomUser, UsersControl, Payment
from rest_framework import generics, mixins, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from .serializers import CustomUserSerializer, PaymentSerializer, PaymentCreateSerializer, ChangePasswordSerializer

User = get_user_model()


class UserLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'
    next_page = 'materials:home'

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
    success_url = reverse_lazy('materials:home')
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


class UserDeleteAPIView(generics.DestroyAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]


class UserListAPIView(ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]


class CustomUserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]


class CustomUserPartialUpdateAPIView(generics.GenericAPIView, mixins.UpdateModelMixin):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class InitUsersControlView(CreateView):
    model = UsersControl
    form_class = UsersControlInitForm
    template_name = 'init_users_control.html'
    context_object_name = 'control'
    success_url = reverse_lazy('materials:home')

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
            return HttpResponseRedirect(reverse_lazy('materials:home'))
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


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = CustomUser
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        print(f"kwargs: {kwargs}")
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            # if not self.object.check_password(serializer.data.get("old_password")):
            #     return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            password = serializer.data.get("new_password")
            user = CustomUser.objects.get(pk=kwargs['pk'])
            user.set_password(password)
            user.save()
            # self.object.set_password(password)
            # self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#############################################################################################################
class CreatePaymentAPIView(generics.CreateAPIView):
    queryset = Payment.objects.all
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]


class DeletePaymentAPIView(generics.DestroyAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]


class PaymentsListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('course', 'lesson', 'cash', 'user', 'created_at')
    ordering_fields = ['course', 'lesson', 'cash', 'user', 'created_at', 'user']

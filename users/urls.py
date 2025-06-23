from django.urls import path
from django.contrib.auth.views import LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshSlidingView
from .views import (RegisterView,
                    UserDeleteView,
                    UserUpdateView, UserLoginView, UserConfirmEmailView,
                    EmailConfirmationSentView, EmailConfirmedView,
                    EmailConfirmationFailedView, UsersControlView, UserForgotPasswordView,
                    UserPasswordResetConfirmView, CustomUserRetrieveAPIView, CreatePaymentAPIView,
                    DeletePaymentAPIView, PaymentsListAPIView, UserCreateAPIView)

from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='materials:home'), name='logout'),
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('payments/', PaymentsListAPIView.as_view(), name='payments'),
    path('add_payment/', CreatePaymentAPIView.as_view(), name='add_payment'),
    path('delete_payment/<int:pk>/', DeletePaymentAPIView.as_view(), name='delete_payment'),
    path('greetings/<int:pk>', RegisterView.as_view(), name='greetings'),
    path("profile/<int:pk>/", CustomUserRetrieveAPIView.as_view(), name="user_profile"),
    path('edit_user/<int:pk>/', UserUpdateView.as_view(), name='edit_user'),
    path("delete_user/<int:pk>/", UserDeleteView.as_view(), name="delete_user"),
    path("control_users/<int:pk>/", UsersControlView.as_view(), name="control_users"),
    path('password_reset/', UserForgotPasswordView.as_view(), name='password_reset'),
    path('set-new-password/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('email_confirmation_sent/', EmailConfirmationSentView.as_view(), name='email_confirmation_sent'),
    path('confirm_email/<str:uidb64>/<str:token>/', UserConfirmEmailView.as_view(), name='confirm_email'),
    path('email_confirmed/', EmailConfirmedView.as_view(), name='email_confirmed'),
    path('confirm_email_failed/', EmailConfirmationFailedView.as_view(), name='email_confirmation_failed'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token_refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
]

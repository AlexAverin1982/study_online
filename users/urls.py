from django.urls import path
from django.contrib.auth.views import LogoutView
# , LoginView
from .views import (RegisterView, UserProfileView, UserDeleteView,
                    UserUpdateView, UserLoginView, UserConfirmEmailView,
                    EmailConfirmationSentView, EmailConfirmedView,
                    EmailConfirmationFailedView, UsersControlView, UserForgotPasswordView,
                    UserPasswordResetConfirmView)

urlpatterns = [
    # path('login/', LoginView.as_view(template_name='login.html', next_page='home'), name='login'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('greetings/<int:pk>', RegisterView.as_view(), name='greetings'),
    path("profile/<int:pk>/", UserProfileView.as_view(), name="user_profile"),
    path('edit_user/<int:pk>/', UserUpdateView.as_view(), name='edit_user'),
    path("delete_user/<int:pk>/", UserDeleteView.as_view(), name="delete_user"),
    path("control_users/<int:pk>/", UsersControlView.as_view(), name="control_users"),
    path('password_reset/', UserForgotPasswordView.as_view(), name='password_reset'),
    path('set-new-password/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path("init_users_control/", InitUsersControlView.as_view(), name="init_users_control"),
    path('email_confirmation_sent/', EmailConfirmationSentView.as_view(), name='email_confirmation_sent'),
    path('confirm_email/<str:uidb64>/<str:token>/', UserConfirmEmailView.as_view(), name='confirm_email'),
    path('email_confirmed/', EmailConfirmedView.as_view(), name='email_confirmed'),
    path('confirm_email_failed/', EmailConfirmationFailedView.as_view(), name='email_confirmation_failed'),
]

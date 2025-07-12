from django.urls import path
from django.contrib.auth.views import LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshSlidingView
from .views import (CustomUserRetrieveAPIView, CreatePaymentAPIView,
                    DeletePaymentAPIView, PaymentsListAPIView, UserCreateAPIView, UserListAPIView, UserDeleteAPIView,
                    CustomUserPartialUpdateAPIView, ChangePasswordView, BuyCourse, CheckCourseBought)

from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    # path('login/', UserLoginView.as_view(), name='login'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='materials:home'), name='logout'),
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('users/', UserListAPIView.as_view(), name='users'),
    path('edit_user/<int:pk>/', CustomUserPartialUpdateAPIView.as_view(), name='edit_user'),
    path('set_password/<int:pk>/', ChangePasswordView.as_view(), name='set_password'),
    path("delete_user/<int:pk>/", UserDeleteAPIView.as_view(), name="delete_user"),
    path('payments/', PaymentsListAPIView.as_view(), name='payments'),
    path('add_payment/', CreatePaymentAPIView.as_view(), name='add_payment'),
    path('delete_payment/<int:pk>/', DeletePaymentAPIView.as_view(), name='delete_payment'),
    path("profile/<int:pk>/", CustomUserRetrieveAPIView.as_view(), name="user_profile"),
    path('token_refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
    path('buy_course/', BuyCourse.as_view(), name='buy_course'),
    path('check_course_bought_ok/<int:user>/<int:course>/', CheckCourseBought.as_view(), name='check_course_bought_ok'),
]

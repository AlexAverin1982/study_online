from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, UsersControl, Payment
from rest_framework import generics, mixins, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from .permissions import IsSuperUser, IsOwnProfile
from .serializers import CustomUserSerializer, PaymentSerializer, PaymentCreateSerializer, ChangePasswordSerializer, \
    CustomUserRestrictedSerializer

User = get_user_model()


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
    permission_classes = [IsAuthenticated, IsSuperUser | IsOwnProfile]


class UserListAPIView(ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]


class CustomUserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated ] #, IsOwnProfile]

    def get_serializer_class(self):
        profile_id = self.kwargs.get('pk')
        if profile_id:
            if profile_id == self.request.user.id:
                return CustomUserSerializer
            else:
                return CustomUserRestrictedSerializer


class CustomUserPartialUpdateAPIView(generics.GenericAPIView, mixins.UpdateModelMixin):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsOwnProfile]

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = CustomUser
    permission_classes = [IsAuthenticated, IsSuperUser | IsOwnProfile]

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

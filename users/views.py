from django.contrib.auth import get_user_model
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from materials.models import Course
from materials.serializers import CourseSerializer
from .models import CustomUser, UsersControl, Payment
from rest_framework import generics, mixins, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from .permissions import IsSuperUser, IsOwnProfile, IsOwner
from .serializers import CustomUserSerializer, PaymentSerializer, PaymentCreateSerializer, ChangePasswordSerializer, \
    CustomUserRestrictedSerializer
import stripe

User = get_user_model()


class UserCreateAPIView(generics.CreateAPIView):
    """
    Регистрация пользователя
    """
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserDeleteAPIView(generics.DestroyAPIView):
    """
    Удаление пользователя
    """
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, IsSuperUser | IsOwnProfile]


class UserListAPIView(ListAPIView):
    """
    Список пользователей
    """
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]


class CustomUserRetrieveAPIView(generics.RetrieveAPIView):
    """
    Данные о пользователе, доступные всем зарегистривовавшимся
    """
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]  # , IsOwnProfile]

    def get_serializer_class(self):
        profile_id = self.kwargs.get('pk')
        if profile_id:
            if profile_id == self.request.user.id:
                return CustomUserSerializer
            else:
                return CustomUserRestrictedSerializer


class CustomUserPartialUpdateAPIView(generics.GenericAPIView, mixins.UpdateModelMixin):
    """
    Частичное обновление данных в своем профиле
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsOwnProfile]

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ChangePasswordView(generics.UpdateAPIView):
    """
    Смена пароля
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
    """
    Оплата урока или курса
    """
    queryset = Payment.objects.all
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]


class DeletePaymentAPIView(generics.DestroyAPIView):
    """
    Удаление оплаты
    """
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]


class PaymentsListAPIView(generics.ListAPIView):
    """
    Список всех платежей
    """
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('course', 'lesson', 'cash', 'user', 'created_at')
    ordering_fields = ['course', 'lesson', 'cash', 'user', 'created_at', 'user']


class CreateCourseProduct(generics.CreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Course.objects.all()
    """
    владелец курса создает на стороннем апи продукт курса для того, чтобы его можно было купить
    
    нужно наименование курса и его
    """

    def post(self, *args, **kwargs):
        user = self.request.user
        print(f"user: {user}")
        course_id = self.request.data.get("course_id")
        """
        проверяем, существует ли указанный курс
        """
        try:
            course = Course.objects.get(id=course_id)
        except ObjectDoesNotExist:
            raise Http404
        """
        проверяем, является ли пользователь владельцем указанного курса
        """
        print(f"\n\ncourse.owner: {course.owner}, type: {type(course.owner)}")
        if not course.owner or course.owner != self.request.user:
            return Response({"message": "Вы не являетесь владельцем указанного курса"})

        print(f"course: {course_id}")
        course_item = Course.objects.get(pk=course_id)

        print(f"\n\nself.request.data: {self.request.data}\n\n")

        # if course_item.product:
        #     return Response({"message": "Такой продукт уже создан"})

        price = self.request.data.get("price")
        obj_price = course_item.price
        if obj_price:
            if price:  # the price specified in request is considered to be more actual than the one in course's field
                course_item.price = price
            else:
                price = course_item.price
        elif price:
            course_item.price = price

        print(f"course: {course_item.name}")
        print(f"desc: {course_item.description}")
        print(f"product: {course_item.product}")

        stripe.api_key = "sk_test_51RjKhk04SatfhYz28u3eQ2qjpF0TFrfc6ePHTK9OzIc7avdYvFAPXqZPZgRWuGTwS4Al2Vwjy9O9Kbg6XkKY9uEP00XPONBjhw"
        # product = stripe.Product.create(name=course_item.name)
        # if product:
        #     course_item.product = product.id

        if price:
            stripe_price = stripe.Price.create(unit_amount=price, currency='rub', product='prod_Sef1YkWqDO7U8n')
            print(f"stripe price: {stripe_price}")
            """
$stripe->prices->create([
  'unit_amount' => 1999,
  'currency' => 'usd',
  'recurring' => ['interval' => 'month'],
  'product' => $product_id,
  'lookup_key' => $your_custom_value
]);                
            """
        course_item.save()

        # print(f"\n\n product: {product}\n\n")

        # if Subscription.objects.filter(user=user, course=course_item).exists():
        #     Subscription.objects.filter(user=user, course=course_item).delete()
        #     message = "подписка удалена"
        # else:
        #     sub = Subscription.objects.create(user=user, course=course_item)
        #     sub.save()
        #     message = "подписка добавлена"

        return Response({"message": "продукт курса создан"})

        # for item in self.request:
        #     print(item)

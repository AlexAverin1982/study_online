from django.contrib.auth import get_user_model
# from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from dotenv import load_dotenv
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse

from materials.models import Course, Lesson
from materials.stripe_api import StripeAPI
from .models import CustomUser, Payment
from rest_framework import generics, mixins, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
# from django.core.exceptions import ObjectDoesNotExist

from .permissions import IsSuperUser, IsOwnProfile, IsOwner, IsAdmin
from .serializers import CustomUserSerializer, PaymentSerializer, PaymentCreateSerializer, ChangePasswordSerializer, \
    CustomUserRestrictedSerializer

User = get_user_model()
load_dotenv()


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
        # print(f"kwargs: {kwargs}")
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


class BuyCourse(generics.CreateAPIView):
    """
    формирование ссылки на сеанс покупки курса с автоматически создаваемой формой покупки картой на сайте stripe
    """
    queryset = Payment.objects.all
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]
    """
    пользователь получает ссылку, переходит по ней, видит цену на курс, вводит в форму данные карты, покупает

    статус сеанса должен поменяться - тогда список купленных курсов у пользователя обновляется 
    """

    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get('course_id', 0)
        if not course_id:
            return Response({"status": 400, "message": "не указан идентификатор покупаемого курса"})

        course = Course.objects.get(id=course_id)
        if course.stripe_price:
            api = StripeAPI()
            payment = Payment.objects.create(user=user, course=course, sum=1000)
            payment.save()
            url = 'http://127.0.0.1:8000' + reverse('users:check_course_bought_ok',
                                                    kwargs={'course': payment.pk, "user": user.id})
            # url = reverse('users:check_course_bought_ok', kwargs={'pk': payment.pk})
            session = api.create_checkout_session(course.stripe_price, success_url=url)

            payment.sum = session.amount_total
            payment.session = session.id
            payment.save()
            """
            для сессии нужно сформировать ссылку, куда пользователь автоматически
            перенаправится для проверки, произошла ли покупка
            в ссылке нужно указать идентификатор оплаты
            """

        else:
            return Response({"status": 400, "message": "у курса не указана стоимость"})

        return Response({"status": 200, "url": session.url})


class CheckCourseBought(generics.RetrieveAPIView):
    """
    После удачной покупки курса пользователь автоматически переходит на этот вид,
    где мы получаем объект оплаты, объект сессии покупки, проверяем ее статус, и если все хорошо -
    обновляем у пользователя список купленных курсов
    """
    queryset = Payment.objects.all
    serializer_class = PaymentCreateSerializer

    # permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        # из ссылки нужно выковырять идентификатор оплаты
        # print(f"kwargs: {kwargs}")
        payment_id = kwargs.get('course')
        payment = get_object_or_404(Payment, id=payment_id)
        api = StripeAPI()
        # print(f"session id: {payment.session}")
        message = "вроде бы ок"

        if payment.session:
            session = api.checkout_session(payment.session)
            message = f"session status: {session.status}; payment status: {session.payment_status}"

            if (session.status == 'complete') and (session.payment_status == 'paid'):
                user_id = kwargs.get('user')
                user = get_object_or_404(CustomUser, id=user_id)
                user.courses_bought.add(payment.course)

        return Response({"status": 200, "message": message})
        # super(CheckCourseBought, self).get(request, *args, **kwargs)


class BuyLesson(generics.CreateAPIView):
    """
    формирование ссылки на сеанс покупки отдельного урока
    с автоматически создаваемой формой покупки картой на сайте stripe
    """
    queryset = Payment.objects.all
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]
    """
    пользователь получает ссылку, переходит по ней, видит цену за урок, вводит в форму данные карты, покупает.
    статус сеанса должен поменяться - тогда список купленных уроков у пользователя обновляется 
    """

    def post(self, request, *args, **kwargs):
        user = self.request.user
        # print(f"\n\n\nrequest.get_host(): {request.get_host()}\n")
        # for item in sorted(dir(request)):
        #     print(item)

        lesson_id = self.request.data.get('lesson_id', 0)
        if not lesson_id:
            return Response({"status": 400, "message": "не указан идентификатор покупаемого урока"})

        lesson = get_object_or_404(Lesson, id=lesson_id)
        if lesson.stripe_price:
            api = StripeAPI()
            payment = Payment.objects.create(user=user, lesson=lesson, sum=1000)
            payment.save()

            # TODO: detect protocol
            url = 'http://' + request.get_host() + reverse('users:check_lesson_bought_ok',
                                                           kwargs={'payment': payment.pk, "user": user.id})

            session = api.create_checkout_session(lesson.stripe_price, success_url=url)

            payment.sum = session.amount_total
            payment.session = session.id
            payment.save()
            """
            для сессии нужно сформировать ссылку, куда пользователь автоматически
            перенаправится для проверки, произошла ли покупка
            в ссылке нужно указать идентификатор оплаты
            """

        else:
            return Response({"status": 400, "message": "у урока не указана стоимость"})

        return Response({"status": 200, "url": session.url})


class CheckLessonBought(generics.RetrieveAPIView):
    """
    После удачной покупки курса пользователь автоматически переходит на этот вид,
    где мы получаем объект оплаты, объект сессии покупки, проверяем ее статус, и если все хорошо -
    обновляем у пользователя список купленных курсов
    """
    queryset = Payment.objects.all
    serializer_class = PaymentCreateSerializer

    # permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        # из ссылки нужно выковырять идентификатор оплаты
        # print(f"kwargs: {kwargs}")
        payment_id = kwargs.get('payment')
        payment = get_object_or_404(Payment, id=payment_id)
        api = StripeAPI()
        # print(f"session id: {payment.session}")
        message = "вроде бы ок"

        if payment.session:
            session = api.checkout_session(payment.session)
            message = f"session status: {session.status}; payment status: {session.payment_status}"

            if (session.status == 'complete') and (session.payment_status == 'paid'):
                user_id = kwargs.get('user')
                user = get_object_or_404(CustomUser, id=user_id)
                user.lessons_bought.add(payment.lesson)

        return Response({"status": 200, "message": message})
        # super(CheckCourseBought, self).get(request, *args, **kwargs)


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

#############################################################################################################

class CreatePeriodicTaskCheckInactiveUsers(generics.GenericAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, *args, **kwargs):
        from datetime import datetime as dt, timedelta
        from users.admin_tools import enable_periodic_task
        enable_periodic_task(every=20,
                             period='seconds',
                             name='check inactive users',
                             task='users.tasks.check_inactive_users',
                             expires=dt.now() + timedelta(seconds=30))

        return Response({"status": 200, "message": "check task in admin tool"})
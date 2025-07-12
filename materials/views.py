from django.shortcuts import get_object_or_404
from django.views import generic
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from materials.models import Course, Lesson, Subscription
from materials.paginators import CoursePaginator, LessonsPaginator
from materials.serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """

       create:
       Добавление обучающего курса

       retrieve:
       Получить информацию по конкретному курсу

       list:
       Список обучающих курсов (опционально - номер страницы с результатами)

       update:
       Обновить информацию по конкретному курсу

       partial_update:
       Частично обновить информацию по конкретному курсу

       delete:
       Удалить курс

    """
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CoursePaginator

    @swagger_auto_schema(method='get', operation_description="Список уроков в курсе")
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        course = self.get_object()

        lessons = course.Уроки.all()
        serializer = LessonSerializer(lessons, many=True, read_only=True)
        permission_classes = [IsAuthenticated, IsOwner]
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsAuthenticated, ~IsModerator, ]
        elif self.action in ['retrieve', 'update']:
            self.permission_classes = (IsAuthenticated, IsModerator,)
        elif self.action in ['destroy']:
            self.permission_classes = (~IsModerator | IsOwner,)
        else:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


##################################################################################################################

class LessonCreateAPIView(generics.CreateAPIView):
    """
    Добавление урока в обучающий курс
    """
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """
    Список всех уроков на всех курсах
    """
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = LessonsPaginator


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Данные конкретного урока
    """
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner | IsModerator]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    Обновить данные урока
    """
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner | IsModerator]


class LessonPartialUpdateAPIView(generics.GenericAPIView, mixins.UpdateModelMixin):
    """
    Частично обновить данные урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner | IsModerator]

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Удалить урок
    """
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


class SubscriptionCreateAPIView(generics.CreateAPIView):
    """
    Добавление/удаление подписки на обновления обучающего курса
    """
    serializer_class = SubscriptionSerializer
    # permission_classes = [IsAuthenticated, ~IsModerator]
    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        user = self.request.user
        # print(f"user: {user}")
        course_id = self.request.data.get("course_id")
        # print(f"course: {course_id}")
        course_item = Course.objects.get(pk=course_id)
        # print(f"course: {course_item}")

        if Subscription.objects.filter(user=user, course=course_item).exists():
            Subscription.objects.filter(user=user, course=course_item).delete()
            message = "подписка удалена"
        else:
            sub = Subscription.objects.create(user=user, course=course_item)
            sub.save()
            message = "подписка добавлена"

        return Response({"message": message})

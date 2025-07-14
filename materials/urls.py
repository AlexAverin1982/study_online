from django.urls import path
from . import views
from materials.apps import MaterialsConfig
from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, CreateCourseProduct, CreateLessonProduct

app_name = MaterialsConfig.name

router = DefaultRouter()
router.register('courses', CourseViewSet, 'courses')

urlpatterns = ([
                   path("add_lesson/", views.LessonCreateAPIView.as_view(), name="add_lesson"),
                   path("lessons/", views.LessonListAPIView.as_view(), name="lessons"),
                   # path("lesson/<int:pk>/", views.LessonRetrieveAPIView.as_view(), name="lesson"),
                   path("lessons/<int:pk>/", views.LessonRetrieveAPIView.as_view(), name="lesson"),
                   path("update_lesson/<int:pk>/", views.LessonPartialUpdateAPIView.as_view(), name="update_lesson"),
                   path("delete_lesson/<int:pk>/", views.LessonDestroyAPIView.as_view(), name="delete_lesson"),
                   path("add_sub/", views.SubscriptionCreateAPIView.as_view(), name="add_sub"),
                   path('create_course_product/', CreateCourseProduct.as_view(), name='create_course_product'),
                   path('create_lesson_product/', CreateLessonProduct.as_view(), name='create_lesson_product'),
               ] + router.urls)

# print(router.urls)
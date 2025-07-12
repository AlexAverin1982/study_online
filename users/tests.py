"""
test crud for lessons
"""
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework.test import force_authenticate

from materials.models import Lesson, Course
from materials.stripe_api import StripeAPI
from materials.views import LessonCreateAPIView
from users.models import CustomUser, Payment
from django.contrib.auth.models import Group
from django.urls import reverse
from http import HTTPStatus

client = APIClient()
#
#
# class LessonTestCase(APITestCase):
#
#     def setUp(self):
#         self.user = CustomUser.objects.create(email='test@example.com')
#
#         self.su = CustomUser.objects.create_user(username="su", email="su@mail.ru", password='123456')
#         self.su.is_active = True
#         self.su.is_admin = True
#         self.su.is_superuser = True
#         self.su.save()
#
#         self.moder = CustomUser.objects.create_user(username="moder", email="moder@mail.ru", password='123456')
#         self.moder.is_active = True
#         self.moder.is_admin = True
#         self.moder.save()
#
#         self.co = CustomUser.objects.create_user(username="co", email="co@mail.ru", password='123456')
#         self.co.is_active = True
#         self.co.save()
#
#         self.lesson = Lesson.objects.create(name='lesson #1', owner=self.co)
#         self.url = reverse('materials:lesson', args=(self.lesson.id,))
#
#         self.student = CustomUser.objects.create_user(username="student", email="student@mail.ru", password='123456')
#         self.student.is_active = True
#         self.student.save()
#
#         moderators = Group.objects.create(name='Moderators')
#         self.moder.groups.add(moderators)
#
#     # def test_anonymous_access(self):
#     #     response = self.client.get(self.url)
#     #     self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
#     #
#     # def test_user_without_permissions(self):
#     #     self.client.force_authenticate(user=self.student)
#     #     response = self.client.get(self.url)
#     #     self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
#     #
#     # def test_moder_access(self):
#     #     self.client.force_authenticate(user=self.moder)
#     #     response = self.client.get(self.url)
#     #     self.assertEqual(response.status_code, HTTPStatus.OK)
#     #
#     # def test_owner_access(self):
#     #     self.client.force_authenticate(user=self.co)
#     #     response = self.client.get(self.url)
#     #     self.assertEqual(response.status_code, HTTPStatus.OK)
#
#     def test_course_CRUD(self):
#         client.force_authenticate(user=self.co)
#         data = {
#             "name": "course 1",
#             "description": "course1 description"
#         }
#         response = client.post('/courses/', data=data)
#         course_id = response.json()['id']
#         course = Course.objects.get(id=course_id)
#
#         data = {
#             "name": "lesson 1",
#             "description": "lesson 1 description",
#             "seq_number": 1,
#             "course": course_id
#         }
#         response = client.post('/add_lesson/', data=data)
#         lesson_id = response.json()['id']
#         lesson = Lesson.objects.get(id=lesson_id)
#         # print(f"lesson owner: {lesson.owner}")
#         client.force_authenticate(user=self.student)
#         response = client.get('/courses/')
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#         """
#         course_id = response.json()[0]['id']
#         response = client.get(f'/courses/{course_id}/')
#         self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
#         response = client.get(f'/lessons/{lesson_id}/')
#         self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
#
#         client.force_authenticate(user=self.co)
#         data = {
#             "description": "course 1 is still without description"
#         }
#         response = client.patch(f'/courses/{course_id}/', data=data)
#         self.assertEqual(response.status_code, HTTPStatus.OK)
#
#         course.id = None
#         course.save()
#         response = client.get('/courses/')
#         course2 = Course.objects.all()[1]
#         response = client.delete(f'/courses/{course2.id}')
#         # print(f"response.status_code: {response.status_code}")
#         self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
#         """
#
#     def test_create_lesson_without_auth(self):
#         data = {
#             "name": 'lesson #2',
#             "description": "test lesson description"
#         }
#         response = self.client.post('/add_lesson/', data=data)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#
#     def test_CRUD_lesson_with_auth(self):
#         data = {
#             "name": 'lesson #2',
#             "description": "test lesson description"
#         }
#
#         client.force_authenticate(user=self.co)
#         response = client.post('/add_lesson/', data=data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         test_lesson = Lesson.objects.filter(name='lesson #2')
#         self.assertTrue(test_lesson.exists())
#         test_lesson = Lesson.objects.get(name='lesson #2')
#         self.assertEqual(test_lesson.description, "test lesson description")
#         lesson_id = test_lesson.id
#         # print(f"lesson_id: {lesson_id}")
#         # for l in Lesson.objects.all():
#         #     print(f"id: {l.id}, name: {l.name}, desc: {l.description}, owner: {l.owner}")
#         response = client.get(f'/lessons/{lesson_id}/')
#         # for item in dir(response):
#         #     print(item)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.json()['description'], "test lesson description")
#         response = client.get('/lessons/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.json().get('count'), 2)
#
#         data = {
#             "description": "still no description..."
#         }
#         response = client.put(f'/update_lesson/{lesson_id}/', data=data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.json()['description'], "still no description...")
#
#         data = {
#             "video": "tralalala"
#         }
#         response = client.put(f'/update_lesson/{lesson_id}/', data=data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         # print(f"\n\nresponse: {response.json()}\n\n")
#         self.assertEqual(response.json()['video'][0], "Разрешается публиковать материалы только с youtube.com")
#         # # print(f"result: {response.json()['video'][0]}")
#         url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1"
#         data = {
#             "video": url
#         }
#         response = client.put(f'/update_lesson/{lesson_id}/', data=data)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.json()['video'], url)
#
#         old_count = Lesson.objects.all().count()
#         response = client.delete(f'/delete_lesson/{lesson_id}/')
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#
#         new_count = Lesson.objects.all().count()
#         # print(f"\n\nnew_count: {new_count}\n\n")
#         self.assertEqual(old_count - 1, new_count)
#         test_lesson = Lesson.objects.filter(name='lesson #2')
#         self.assertTrue(not test_lesson.exists())
#
#
#     def test_sub_unsub(self):
#         client.force_authenticate(user=self.co)
#         data = {
#             "name": "course 1",
#             "description": "course1 description"
#         }
#         response = client.post('/courses/', data=data)
#         course_id = response.json()['id']
#
#         data = {
#             "course_id": course_id
#         }
#
#         client.force_authenticate(user=self.student)
#         response = client.post('/add_sub/', data=data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.json()['message'], 'подписка добавлена')
#         response = client.post('/add_sub/', data=data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.json()['message'], 'подписка удалена')

class PaymentTestCase(APITestCase):
    def setUp(self):
        self.api = StripeAPI()
        self.user = CustomUser.objects.create(email='test@example.com')

        self.su = CustomUser.objects.create_user(username="su", email="su@mail.ru", password='123456')
        self.su.is_active = True
        self.su.is_admin = True
        self.su.is_superuser = True
        self.su.save()

        self.moder = CustomUser.objects.create_user(username="moder", email="moder@mail.ru", password='123456')
        self.moder.is_active = True
        self.moder.is_admin = True
        self.moder.save()

        self.co = CustomUser.objects.create_user(username="co", email="co@mail.ru", password='123456')
        self.co.is_active = True
        self.co.save()

        # self.lesson = Lesson.objects.create(name='lesson #1', owner=self.co)
        # self.url = reverse('materials:lesson', args=(self.lesson.id,))

        self.student = CustomUser.objects.create_user(username="student", email="student@mail.ru", password='123456')
        self.student.is_active = True
        self.student.save()

        client.force_authenticate(user=self.co)
        data = {
            "name": "course 1",
            "description": "course1 description"
        }
        response = client.post('/courses/', data=data)
        course_id = response.json()['id']
        self.course = Course.objects.get(id=course_id)

    def test_payment(self):
        payment = Payment.objects.create(user=self.user, course=self.course, sum=10000)
        payment.save()
        print(f"\n\npayment.pk: {payment.pk}")
        url = 'http://127.0.0.1:8000' + reverse('users:check_course_bought_ok', kwargs={'pk': payment.pk})
        print(f"url: {url}\n\n")

        session = self.api.create_checkout_session('price_1RjL8804SatfhYz2xG37YPoJ', url)
        payment.sum = session.amount_total
        payment.session = session.id
        payment.save()

        print(f"success_url: {session.success_url}\n\n")


        # self.api.set_session_success_url(session.id, url)


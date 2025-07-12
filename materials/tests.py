"""
test crud for lessons
"""
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework.test import force_authenticate

from materials.models import Lesson, Course, Subscription
from materials.views import LessonCreateAPIView
from users.models import CustomUser


client = APIClient()

class LessonTestCase(APITestCase):

    def setUp(self):
        user = CustomUser.objects.create_user(username="user1", email="user1@mail.ru", password='123456')
        user.is_active = True
        user.save()


    def test_create_lesson_without_auth(self):
        data = {
            "name": "test_lesson",
            "description": "test lesson description"
        }
        response = self.client.post('/add_lesson/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_CRUD_lesson_with_auth(self):
        data = {
            "name": "test_lesson",
            "description": "test lesson description"
        }


        client.force_authenticate(user=CustomUser.objects.get(username='user1'))
        response = client.post('/add_lesson/', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_lesson = Lesson.objects.filter(name='test_lesson')
        self.assertTrue(test_lesson.exists())
        test_lesson = test_lesson[0]
        self.assertEqual(test_lesson.description, "test lesson description")
        lesson_id = test_lesson.id
        response = client.get('/lessons/', pk=lesson_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('results')[0]['description'], "test lesson description")
        response = client.get('/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('count'), 1)

        data = {
            "description": "still no description..."
        }
        response = client.put(f'/update_lesson/{lesson_id}/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['description'], "still no description...")
        # print(response.json()['description'])

        data = {
            "video": "tralalala"
        }
        response = client.put(f'/update_lesson/{lesson_id}/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['video'][0], "Разрешается публиковать материалы только с youtube.com")
        # print(f"result: {response.json()['video'][0]}")
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1"
        data = {
            "video": url
        }
        response = client.put(f'/update_lesson/{lesson_id}/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['video'], url)
        # self.assertEqual(response.json()['video'][0], "Разрешается публиковать материалы только с youtube.com")

        old_count = Lesson.objects.all().count()
        response = client.delete(f'/delete_lesson/{lesson_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        new_count = Lesson.objects.all().count()
        self.assertEqual(old_count - 1, new_count)
        test_lesson = Lesson.objects.filter(name='test_lesson')
        self.assertTrue(not test_lesson.exists())


    def test_subscriptions_CRUD(self):
        data = {
            "name": "test_course",
            "description": "a course to subscribe to"
        }

        user = CustomUser.objects.get(username='user1')
        client.force_authenticate(user=user)
        response = client.post('/courses/', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course = Course.objects.get(name="test_course")

        data = {
            "user": user,
            "course_id": course.id
        }
        response = client.post('/add_sub/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Subscription.objects.filter(user_id=user.id).filter(course_id=course.id).exists())
        self.assertEqual(response.json()['message'], 'подписка добавлена')

        response = client.post('/add_sub/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(not Subscription.objects.filter(user_id=user.id).filter(course_id=course.id).exists())
        self.assertEqual(response.json()['message'], 'подписка удалена')

        # print(f"result: {response.json()}")

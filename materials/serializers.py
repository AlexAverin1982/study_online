from rest_framework import serializers

from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(source='Уроки', many=True)

    def get_lessons_count(self, obj):
        return obj.Уроки.count()

    def get_lessons(self, obj):
        return obj.Уроки.order_by('seq_number')

    class Meta:
        model = Course
        fields = '__all__'


from rest_framework import serializers

from .models import Course, Lesson, Subscription
from .validators import validate_lesson_video_link_source


class LessonSerializer(serializers.ModelSerializer):
    video = serializers.URLField(validators=[validate_lesson_video_link_source], required=False)

    class Meta:
        model = Lesson
        fields = '__all__'



class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    you_have_sub = serializers.SerializerMethodField()
    lessons = LessonSerializer(source='Уроки', many=True, read_only=True)

    def get_lessons_count(self, obj):
        return obj.Уроки.count()

    def get_lessons(self, obj):
        return obj.Уроки.order_by('seq_number')

    def get_you_have_sub(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            return Subscription.objects.filter(user=user, course=obj).exists()
        else:
            return False

    class Meta:
        model = Course
        fields = "__all__"

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

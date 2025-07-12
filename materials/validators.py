from rest_framework.serializers import ValidationError

def validate_lesson_video_link_source(value):
    val = str(value).lower()
    if (val.find('youtube.com\\') == -1) and (val.find('youtube.com/') == -1):
        raise ValidationError("Разрешается публиковать материалы только с youtube.com")

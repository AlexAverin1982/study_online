from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from materials.models import Course, Lesson
from .models import CustomUser, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(source='Платежи', many=True, required=False)

    class Meta:
        model = CustomUser
        fields = '__all__'

    def get_payments(self, obj):
        return obj.Платежи.order_by('-created_at')

class CustomUserRestrictedSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'avatar', 'city']



class PaymentCreateSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(), slug_field='id')
    course = serializers.SlugRelatedField(queryset=Course.objects.all(), slug_field='id', allow_null=True)
    lesson = serializers.SlugRelatedField(queryset=Lesson.objects.all(), slug_field='id', allow_null=True,
                                          allow_empty=True)


    class Meta:
        model = Payment
        fields = '__all__'

    def validate(self, fields):
        user_id = fields.get['lesson']
        CustomUser.objects.get(id=user_id)
        lesson_id = fields.get('lesson')
        course_id = fields.get('course')
        sum = fields.get('sum', 0)
        if lesson_id:
            if course_id:
                lesson = Lesson.objects.get(id=lesson_id)
                if lesson.course != course_id:
                    raise serializers.ValidationError("Курс оплаченного урока указан неверно")
            else:
                raise serializers.ValidationError("Курс оплаченного урока не указан")
        else:
            if not course_id:
                raise serializers.ValidationError(
                    "Необходимо указать либо оплачиваемый курс, либо курс и входящий в него урок.")
        if sum <= 0:
            raise serializers.ValidationError("Сумма платежа не указана или указана неверно.")
        # print(f"sum---------------------------{sum}")
        return fields


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Добавление пользовательских полей в токен
        token['username'] = user.username
        token['email'] = user.email

        return token

class ChangePasswordSerializer(serializers.Serializer):
    model = CustomUser

    """
    Serializer for password change endpoint.
    """
    # old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
from rest_framework import serializers
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # 指定模型类
        model = User
        # 指定字段
        fields = '__all__'
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }
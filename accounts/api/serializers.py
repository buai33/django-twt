from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import exceptions

# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ('url', 'username', 'email')

# Another Serializer method
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    # 验证用户是否存在
    def validate(self, data):
        if not User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                "username": "User does not exist."
            })
        return data


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=3)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


    # will be called when is_valid() is called
    def validate(self, data):
        # same as User.objects.filter(username__iexact=data['username']).exists(）
        # 忽略大小写一个个比过去，效率低 => 存储时就都转化成小写储存
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                "username": "This username has been occupied."
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                "email": "This email address has been occupied."
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        user = User.objects.create_user(
            username = username,
            email = email,
            password = password,
        )
        return user
# from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import (
    UserSerializer,
    LoginSerializer,
    SignupSerializer,
)
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate,
)


# through /api/users/1/ 访问the first user. Can use ReadOnlyModelViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class AccountViewSet(viewsets.ViewSet):

    serializer_class = SignupSerializer
    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    def login(self, request):

        # get username and password from request.
        '''
        request.data['username']
        request.data['password']
        Use django LoginSerializer to check whether username/password is null.
        '''
        # 'GET' method, use request.query_params -> data
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check the input.",
                "errors": serializer.errors,
            }, status=400)

        # validation OK, login
        username = serializer.validated_data['username'] #专业做法从valid之后的data取
        password = serializer.validated_data['password']

        # queryset = User.objects.filter(username=username)
        # print(queryset.query)
        # 可以放到serializers里验证用户是否存在
        # if not User.objects.filter(username=username).exists():
        #     return  Response({
        #         "success": False,
        #         "message": "User does not exist."
        #     }, status=400)

        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "Username and password does not match.",
            }, status=400)

        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check the input",
                "errors": serializer.errors,
            }, status=400)

        user = serializer.save()
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        }, status=201)



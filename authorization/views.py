from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from authorization.models import User
from authorization.serializers import *

class UserInfo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=None)
        queryset = User.objects.select_related().get(id=user.id)
        serializer = UserSerializer(queryset, many=False)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class UsernameDuplicationCheck(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        try:
            check = User.objects.get(username=username)
        except User.DoesNotExist:
            check = None
        if check:
            return Response(status=status.HTTP_226_IM_USED)
        else:
            return Response(status=status.HTTP_202_ACCEPTED)

class EmailDuplicationCheck(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data['email']
        try:
            check = User.objects.get(email=email)
        except User.DoesNotExist:
            check = None
        if check:
            return Response(status=status.HTTP_226_IM_USED)
        else:
            return Response(status=status.HTTP_202_ACCEPTED)

class SignUp(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        email = request.data['email']
        password = request.data['password']
        allow_send_email = request.data['allow_send_email']

        user = User(username=username, email=email, password=password, allow_send_email=allow_send_email)
        user.save()

        return Response(status=status.HTTP_200_OK)


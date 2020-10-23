from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers

from rest_auth.registration.serializers import RegisterSerializer as RestRegisterSerializer

from django.contrib.auth import get_user_model

from allauth.account.adapter import get_adapter
from allauth.account import app_settings as allauth_settings
from allauth.account.utils import setup_user_email

from .models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=16,
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED
    )
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password = serializers.CharField(write_only=True)
    allow_send_email = serializers.BooleanField() 
    
    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password': self.validated_data.get('password', ''),
            'email': self.validated_data.get('email', ''),
            'allow_send_email': self.validated_data.get('allow_send_email', False)
        }
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.allow_send_email = self.cleaned_data['allow_send_email']
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user


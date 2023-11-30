from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import User


class RegisterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']
        extra_kwargs = {'phone_number': {"write_only": True}}


class VerificationCodeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'verification_code']
        extra_kwargs = {'verification_code': {"write_only": True}}


class ResendVerificationCodeModelSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=9)

    class Meta:
        model = User
        fields = ['phone_number']
        extra_kwargs = {'phone_number': {"write_only": True}}


class LogoutModelSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, data):
        self.token = data['refresh_token']
        return data

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError(
                'Token is expired or invalid'
            )

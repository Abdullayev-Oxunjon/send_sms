from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from app.models import User
from app.serializers import RegisterModelSerializer, VerificationCodeModelSerializer, LogoutModelSerializer, \
    ResendVerificationCodeModelSerializer
from app.utils import genereation_verification_code, send_sms


# Create your views here.


class RegisterAPIView(APIView):
    serializer_class = RegisterModelSerializer

    @swagger_auto_schema(
        request_body=RegisterModelSerializer,
        responses={
            status.HTTP_201_CREATED: "Succesfully registered",
            status.HTTP_400_BAD_REQUEST: "Invalid credentials",
        }
    )
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            phone_number = serializer.validated_data['phone_number']
            verification_code = genereation_verification_code()
            exprition_time = timezone.now() + timezone.timedelta(minutes=1)
            serializer.save(verification_code=verification_code, activation_key_expires=exprition_time)
            send_sms(message=f"Tasdiqlash kodi: {verification_code}", recipient=phone_number)
            message = "Tasdiqlash kodi yuborildi. Iltimos SMS orqali tasdiqlab yuboring."
            return Response(data={'message': message}, status=status.HTTP_201_CREATED)
        else:
            if User.objects.filter(phone_number=request.data['phone_number']).exists():
                user = User.objects.get(phone_number=request.data['phone_number'])

                verification_code = genereation_verification_code()
                exprition_time = timezone.now() + timezone.timedelta(minutes=1)
                user.verification_code = verification_code
                user.activation_key_expires = exprition_time
                user.save()
                send_sms(message=f"Tasdiqlash kodi: {verification_code}",
                         recipient=request.data['phone_number'])
                message = "Tasdiqlash kodi yuborildi. Iltimos SMS orqali tasdiqlab yuboring."
                return Response(data={'message': message}, status=status.HTTP_200_OK)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerificationCodeAPIView(CreateAPIView):
    serializer_class = VerificationCodeModelSerializer

    def post(self, request, *args, **kwargs):
        phone_number = request.data['phone_number']
        verification_code = request.data['verification_code']
        try:
            instance = User.objects.get(phone_number=phone_number,
                                        verification_code=verification_code)
            if instance.activation_key_expires > timezone.now():
                instance.is_active = True
                instance.save()
                refresh = RefreshToken.for_user(instance)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                return Response(data={'message': "Bu foydalnuvchi muvaffaqiyatli tasdiqlandi",
                                      'access_token': access_token,
                                      'refresh_token': refresh_token},
                                status=status.HTTP_200_OK)

            # elif instance.is_active:
            #     return Response(data={'message': "Bu foydalanuvchi allaqachon tasdiqlangan"},
            #                     status=status.HTTP_400_BAD_REQUEST)
            elif instance.activation_key_expires > timezone.now() or instance.verification_code != verification_code:
                return Response({'message': 'Tasdiqlash kod muddati tugagan yoki noto\'g\'ri tasdiqlash kod.'},
                                status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'Noto\'g\'ri tasdiqlash kod yoki phone_number.'},
                            status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(GenericAPIView):
    serializer_class = LogoutModelSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={'message': 'Siz muvaffaqiyatli tizimdan  chiqdingiz.'},
            status=status.HTTP_204_NO_CONTENT)


class ResendVerificationAPIView(CreateAPIView):
    serializer_class = ResendVerificationCodeModelSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']

            # Check if user with the provided phone number exists
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                return Response(data={'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the previous verification code has expired
            if user.activation_key_expires > timezone.now():
                return Response(data={'message': 'Previous verification code is still valid.'},
                                status=status.HTTP_400_BAD_REQUEST)

            # Generate a new verification code and update expiration time
            verification_code = genereation_verification_code()
            expiration_time = timezone.now() + timezone.timedelta(minutes=1)
            user.verification_code = verification_code
            user.activation_key_expires = expiration_time
            user.save()

            # Send the new verification code via SMS
            send_sms(message=f"Tasdiqlash kodi: {verification_code}", recipient=phone_number)

            return Response(data={'message': 'Verification code resent successfully.'},
                            status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app.views import RegisterAPIView, VerificationCodeAPIView, LogoutAPIView, ResendVerificationAPIView

urlpatterns = [
    path("register", RegisterAPIView.as_view(), name="register"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('verification_code/', VerificationCodeAPIView.as_view(), name="verification_code"),
    path('resend_verification_code/', ResendVerificationAPIView.as_view(), name="resend_verification_code"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

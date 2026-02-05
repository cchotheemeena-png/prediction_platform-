from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP, User
from .serializers import RegisterSerializer, LoginSerializer, OTPVerifySerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = OTP.objects.create(user=user, channel='phone')
            otp.generate_otp()
            otp.save()
            return Response({'user_id': str(user.id), 'message': 'OTP sent'})
        return Response(serializer.errors, status=400)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            try:
                otp = OTP.objects.get(
                    user__id=serializer.validated_data['user_id'],
                    key=serializer.validated_data['otp'],
                    is_used=False
                )
                otp.is_used = True
                otp.save()
                user = User.objects.get(id=serializer.validated_data['user_id'])
                user.phone_verified = True
                user.save()
                return Response({'message': 'Verified', 'user_id': str(user.id)})
            except OTP.DoesNotExist:
                return Response({'error': 'Invalid OTP'}, status=400)
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        if user and user.phone_verified:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=400)

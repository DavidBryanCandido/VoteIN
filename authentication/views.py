from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import CustomUser
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

class ProtectedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'message': f'Hello, {request.user.first_name}! This is a protected route.'})

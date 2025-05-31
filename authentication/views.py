from django.shortcuts import render
from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from .models import CustomUser, Position, PartyList, Election
from .serializers import RegisterSerializer, PositionSerializer, PartyListSerializer, ElectionSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from typing import Any
from .rate_limit import rate_limit

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    @rate_limit('register', limit=3, period=60)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ProtectedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'message': f'Hello, {request.user.first_name}! This is a protected route.'})

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all() if hasattr(Position, 'objects') else None
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated]

class PartyListViewSet(viewsets.ModelViewSet):
    queryset = PartyList.objects.all() if hasattr(PartyList, 'objects') else None
    serializer_class = PartyListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class ElectionViewSet(viewsets.ModelViewSet):
    queryset = Election.objects.all() if hasattr(Election, 'objects') else None
    serializer_class = ElectionSerializer
    permission_classes = [permissions.IsAuthenticated]

from django.shortcuts import render
from rest_framework.views import APIView
from .models import User
from .serializers import RegisterSerializer, ChangePasswordSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin 

# Create your views here.
class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            response_payload = {
                "status": "success",
                "message": "Account created successfully. Welcome to PocketTracker",
                "data": {
                    'email': user.email,
                    'name': user.name,
                }
            }
            return Response(response_payload, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user

        serializer = ChangePasswordSerializer(instance=user, data=request.data, context={'user':user})

        if serializer.is_valid():
            serializer.save()
            return Response("Password updated successfully", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
    

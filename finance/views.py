from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework import permissions, status
from rest_framework.response import Response  
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from .models import Account, AccountType
from .serializers import AccountTypeSerializer, AccountSerializer

# Create your views here.
def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the post
        return obj.user == request.user


class ListAccountTypesView(GenericAPIView, ListModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class AccountListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        account = Account.objects.filter(user=user)

        serializer = AccountSerializer(account, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = AccountSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountUpdateDeleteView(GenericAPIView, UpdateModelMixin, DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

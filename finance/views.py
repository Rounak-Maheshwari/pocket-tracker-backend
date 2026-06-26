from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework import permissions, status
from rest_framework.response import Response  
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from .models import Account, AccountType, Transaction, TransactionTypeCategory, TransactionType
from .serializers import AccountTypeSerializer, AccountSerializer, TransactionTypeCategorySerializer, TransactionTypeSerializer, TransactionSerializer

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
        user=request.user

        serializer = AccountSerializer(data=request.data, context={'user': user})

        if serializer.is_valid():
            serializer.save(user=user)
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
    

class TransactionTypeListView(GenericAPIView, ListModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class TransactionCategoryListView(GenericAPIView, ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionTypeSerializer

    def get_queryset(self):
        queryset = TransactionTypeCategory.objects.all()

        type_filter = self.request.query_params.get('type')

        if type_filter:
            queryset = queryset.filter(transaction_type__name = type_filter.upper())
        
        return queryset


    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    

class TransactionCreateListView(GenericAPIView, CreateModelMixin, ListModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)

        type_filter = self.request.query_params.get("type")

        if type_filter:
            queryset = queryset.filter(transaction_type__name=type_filter.upper())
        return queryset


    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class TrnasactionUpdateDeleteView(GenericAPIView, UpdateModelMixin, DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def perform_delete(self, instance):
        transaction = self.instance
        transaction_type = transaction.transaction_type
        amount = transaction.amount
        from_account = transaction.from_account
        to_account = transaction.to_account

        if transaction_type.name == 'EXPENSE':
            if from_account and from_account.account_type in ['CASH', 'BANK']:
                from_account.balance += amount
                print('amount', amount)
                print('from_account balance: ', from_account.balance)
                from_account.save()
            elif from_account and from_account.account_type in ['CREDIT CARD', 'LOAN/DEBT']:
                from_account.due_amount -= amount
                from_account.save()
        elif transaction_type.name == 'INCOME':
            if to_account and to_account.account_type in ['CASH', 'BANK']:
                to_account.balance -= amount
                to_account.save()
            # in the income transaction we don't have to check for if to_account is a CREDIT account as we have made it in such a way that the CREDIT CARD cannot have a income.
        elif transaction_type.name == 'TRANSFER':
            if (from_account and to_account):
                # first we need to check if the from account is a bank account or a debt account so have to perform the reverse transactions accordingly.
                if from_account.account_type in ['BANK', 'CASH']:
                    from_account.balace += amount
                    from_account.save()
                elif from_account.account_type in ['CREDIT CARD', 'LOAN/DEBT']:
                    from_account.due_amount -= amount
                    from_account.save()

                # similarly for to account as well.
                if to_account.account_type in ['BANK', 'CASH']:
                    to_account.balace -= amount
                    to_account.save()
                elif to_account.account_type in ['CREDIT CARD', 'LOAN/DEBT']:
                    to_account.due_amout += amount
                    to_account.save()

        transaction.delete()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework import permissions, status
from rest_framework.response import Response  
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from .models import Account, AccountType, Transaction, TransactionTypeCategory, TransactionType
from .serializers import AccountTypeSerializer, AccountSerializer, TransactionTypeCategorySerializer, TransactionTypeSerializer, TransactionSerializer
from django.db.models import Sum

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
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")
        if type_filter:
            queryset = queryset.filter(transaction_type__name=type_filter.upper())
        if month and year:
            start_date = f"{year}-{month}-01"
            end_date = f"{year}-{month}-30"
            queryset = queryset.filter(event_date__range=(start_date, end_date))
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
    

class FinancialAnalyticsListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        # for getting the account details
        bank_accounts = Account.objects.filter(user=request.user).filter(account_type__name="BANK")
        cash_accounts = Account.objects.filter(user=request.user).filter(account_type__name="CASH")
        credit_accounts = Account.objects.filter(user=request.user).filter(account_type__name="CREDIT CARD")

        bank_accounts_total = bank_accounts.aggregate(total=Sum('balance'))
        cash_accounts_total = cash_accounts.aggregate(total=Sum('balance'))
        credit_accounts_dues = credit_accounts.aggregate(total=Sum('due_amount'))

        bank_accounts_total_balance = bank_accounts_total.get('total') or 0
        cash_accounts_total_balance = cash_accounts_total.get('total') or 0
        credit_accounts_total_balance = credit_accounts_dues.get('total') or 0

        total_liquid_flow = bank_accounts_total_balance + cash_accounts_total_balance

        # get the list of bank accounts to display on frontend.
        all_banks_detils = bank_accounts.values('name', 'balance')
        all_cash_details = cash_accounts.values('name', 'balance')
        all_credit_details = credit_accounts.values('name', 'fixed_credit_limit', 'due_amount')



        queryset = Transaction.objects.filter(user=self.request.user)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(event_date__range=(start_date, end_date))
        
        inflows = queryset.filter(transaction_type__name='INCOME')
        expenses = queryset.filter(transaction_type__name="EXPENSE")

        total_inflow = inflows.aggregate(total=Sum('amount'))
        total_expense = expenses.aggregate(total=Sum('amount')) 

        total_inflow_amount = total_inflow.get('total') or 0
        total_expense_amount = total_expense.get('total') or 0

        savings = total_inflow_amount - total_expense_amount

        sql_category_summary = queryset.filter(transaction_type__name='EXPENSE').values('category__name').annotate(total_spent=Sum('amount'))

        # to get the category set according to the queryset filter.
        category_breakdown = []
        for row in sql_category_summary:
            category_name = row.get('category__name')
            total_spent = row.get('total_spent') or 0

            percentage = 0.0
            if total_expense_amount > 0:
                percentage = round((total_spent / total_expense_amount) * 100, 2)

            category_breakdown.append({
                "name": category_name,
                "total": total_spent,
                "percentage": percentage
            })
            
        dashboard_payload = {
            "filter_info": {
                "start_date": request.query_params.get('start_date'),
                "end_date": request.query_params.get('end_date')
            },
            "analytics": {
                "savings": savings,
                "total_inflows": total_inflow_amount,
                "total_expenses": total_expense_amount
            }, 
            "accounts_info": {
                "total_liquid_flow": total_liquid_flow,
                "total_credit_dues": credit_accounts_total_balance,
                "total_bank_account_balance": bank_accounts_total_balance,
                "total_cash_account_balance": cash_accounts_total_balance
            },
            "lifetime_accounts": {
                "bank_lists": all_banks_detils,
                "cash_lists": all_cash_details,
                "credit_card_lists": all_credit_details,
            },
            'category_breakdown': category_breakdown,
            
        }

        return Response(dashboard_payload, status=status.HTTP_200_OK)










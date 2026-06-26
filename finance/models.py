from django.db import models
from authentication.models import User

# Create your models here.
class AccountType(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=100)
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE, related_name='accounts')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True, null=True)
    # additional fields to check if the account is a debt account.
    due_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    fixed_credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available_credit(self):
        if self.account_type.name in ['CREDIT CARD', 'LOAN/DEBT']:
            return self.fixed_credit_limit - self.due_amount 
        return 0.00

    def __str__(self):
        if self.account_type.name == 'CREDIT CARD' or self.account_type.name == 'LOAN/DEBT':
            return f"{self.user.name} - {self.user.email} --------- max limit: {self.fixed_credit_limit} ---- due_amount: {self.due_amount} ---- balance limit: {self.available_credit}"
        return f"{self.user.name} - {self.user.email} -------- Rs {self.balance}"
    

class TransactionType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

class TransactionTypeCategory(models.Model):
    name = models.CharField(max_length=100)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE, related_name="transaction_type_category")

    def __str__(self):
        return f"{self.id} - Category {self.transaction_type.name} ----------------- {self.name}"
    

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="departure_account", blank=True, null=True)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    note = models.TextField(max_length=150, null=True, blank=True)
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name="arriving_account")
    category = models.ForeignKey(TransactionTypeCategory, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True)
    event_date = models.DateField()

    def __str__(self):
        return f"Userid: {self.user.id} ----- User: {self.user.name} ----------- transaction_type: {self.transaction_type.name} ----------------- amount: {self.amount}"

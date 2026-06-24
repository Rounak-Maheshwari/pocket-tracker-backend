from django.contrib import admin
from .models import Account, AccountType, Transaction, TransactionType, TransactionTypeCategory

# Register your models here.
admin.site.register(Account)
admin.site.register(AccountType)
admin.site.register(TransactionType)
admin.site.register(Transaction)
admin.site.register(TransactionTypeCategory)
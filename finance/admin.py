from django.contrib import admin
from .models import Account, AccountType

# Register your models here.
admin.site.register(Account)
admin.site.register(AccountType)
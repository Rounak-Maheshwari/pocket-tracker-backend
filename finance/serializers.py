from rest_framework import serializers
from .models import Account, AccountType

class AccountTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountType 
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    account_type_details = AccountTypeSerializer(source="account_type", read_only=True)
    balance = serializers.ReadOnlyField()
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Account
        fields = ["id", "user", "name", "account_type", "account_type_details", "balance", "created_at", "updated_at"]

    def validate_balance(self, value):
        if value < 0:
            return serializers.ValidationError("Balance cant be less than 0")
        return value
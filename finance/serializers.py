from rest_framework import serializers
from .models import Account, AccountType, Transaction, TransactionType, TransactionTypeCategory

class AccountTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountType 
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    account_type_details = AccountTypeSerializer(source="account_type", read_only=True)
    balance = serializers.ReadOnlyField()
    user = serializers.ReadOnlyField(source='user.email')
    available_credit = serializers.ReadOnlyField()

    class Meta:
        model = Account
        fields = ["id", "user", "name", "account_type", "account_type_details", "balance", "created_at", "updated_at", "fixed_credit_limit", "due_amount", "available_credit"]

    def validate(self, attr):
        balance = attr.get("balance")
        account_type = attr.get('account_type')
        due_amount = attr.get('due_amount')
        fixed_credit_limit = attr.get('fixed_credit_limit')
        available_credit = attr.get('available_credit')

        if balance and balance < 0:
            return serializers.ValidationError("Balance cant be less than 0")
        if account_type.name in ['CREDIT CARD', 'LOAN/DEBT']:
            if due_amount > fixed_credit_limit or (available_credit != None and available_credit > fixed_credit_limit):
                raise serializers.ValidationError("Due amount or Available credit can't be grether than the Fixed Credit")
        return attr    
    
    def create(self, validated_data):
        account = Account.objects.create(**validated_data)
        account.save()

        return account

class TransactionTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionType
        fields = "__all__"


class TransactionTypeCategorySerializer(serializers.ModelSerializer):
    transaction_type = TransactionTypeSerializer(read_only=True)

    class Meta:
        model = TransactionTypeCategory
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type_details = TransactionTypeSerializer(source='transaction_type', read_only=True)
    transaction_type_category_details = TransactionTypeCategorySerializer(source='transaction_type_category', read_only=True)
    user = serializers.ReadOnlyField(source='user.email')
    from_account_details = AccountSerializer(source='from_account', read_only=True)
    to_account_details = AccountSerializer(source='to_account', read_only=True)


    # for getting just the id of the data when the user sends a post request
    transaction_type = serializers.PrimaryKeyRelatedField(queryset=TransactionType.objects.all(), required=True, allow_null=False)
    transaction_type_category = serializers.PrimaryKeyRelatedField(queryset=TransactionTypeCategory.objects.all(), required=False, allow_null = True)
    from_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)
    to_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Transaction
        fields = ["id", "user", "amount", "note", "event_date", "from_account", "from_account_details", "to_account", "to_account_details", "transaction_type", "transaction_type_details", "transaction_type_category", "transaction_type_category_details"]

    def validate(self, attr):
        
        amount = attr.get('amount')
        from_account = attr.get('from_account')
        to_account = attr.get('to_account')
        transaction_type = attr.get('transaction_type')

        # checking that if the transaction type is 'EXPENSE' or 'TRANSFER' then there must be from_account else this will raise an error
        if transaction_type.name in "EXPENSE" and from_account == None:
            raise serializers.ValidationError("You hanven't selected an account to debit money")
        if transaction_type.name == 'INCOME' and to_account == None:
            raise serializers.ValidationError("You can't have an income without selecting an account.")
        if transaction_type.name in "TRANSFER" and (from_account == None or to_account == None):
            raise serializers.ValidationError("You hanven't selected an account.")

        if from_account.account_type.name in ['CREDIT CARD', 'LOAN/DEBT']:
            fixed_credit_limit = attr.get('fixed_credit_limit')
            available_credit = from_account.available_credit
            print("available_credit:", available_credit)
            due_amount = attr.get('due_amount')
        
        # checking that we are not transfering money from and to the same account like transfering account A money to account A.
        if transaction_type.name == 'TRANSFER' and from_account.id == to_account.id:
            raise serializers.ValidationError("You can't transfer money to the same account.")
        

        # CHECKING THAT THE USER CAN'T TRANSFER MONEY FROM CASH ACCOUNT TO ANY OTHER ACCOUNT.
        if from_account and from_account.account_type.name == 'CASH':
            if transaction_type.name == 'EXPENSE' and amount > from_account.balance:
                raise serializers.ValidationError("Insufficient Balance")
            elif transaction_type.name == 'TRANSFER': 
                raise serializers.ValidationError("Can't transfer money from cash account.")

        # checking in case of spending/transfering money from bank or cash then the amount should not exceeds the bank/cash account balance.
        if from_account and from_account.account_type.name == 'BANK':
            if transaction_type.name == 'EXPENSE' or transaction_type.name == 'TRANSFER' and amount > from_account.balance:
                raise serializers.ValidationError("Insufficient Balance")

        # checking in case of spending money from Credit Cards the amount of money should not exceeds the available limit.
        if from_account and from_account.account_type.name in ['CREDIT CARD', 'LOAN/DEBT']:
            if (transaction_type.name == "EXPENSE" or transaction_type.name == 'TRANSFER') and amount > available_credit:
                raise serializers.ValidationError('Ammount exceeds the available Credit limit.')
        
        # in case of income we can't have an income in the DEBT accounts (CREDIT/LOAN)
        if to_account and to_account.account_type.name in ['CREDIT CARD', 'LOAN/DEBT'] and transaction_type.name == 'INCOME':
            raise serializers.ValidationError("You can't have income in the Credit Card or Loan Account.")

        return attr
    
    def create(self, validated_data):
        user = self.context.get('request').user

        transaction_type = validated_data.get("transaction_type")
        amount = validated_data.get('amount')
        from_account = validated_data.get("from_account")
        to_account = validated_data.get("to_account")

        if transaction_type.name == 'EXPENSE':
            if from_account.account_type.name in ['CREDIT CARD', 'LOAN']:
                from_account.due_amount += amount
                from_account.save()
            elif from_account.account_type.name in ['BANK', 'CASH']:    
                from_account.balance -= amount
                from_account.save()
        elif transaction_type.name == "INCOME":
            to_account.balance += amount
            to_account.save()

        elif transaction_type.name == "TRANSFER":
            if from_account.account_type.name in ['CREDIT CARD', 'LOAN']:
                from_account.due_amount += amount
                from_account.save()
            elif from_account.account_type.name in ['BANK']:    
                from_account.balance -= amount
                from_account.save()

            if to_account.account_type.name in ['CREDIT CARD', 'LOAN']:
                to_account.due_amount -= amount
                to_account.save()
            elif to_account.account_type.name in ['BANK', "CASH"]:
                to_account.balance += amount
                to_account.save()

        transaction = Transaction.objects.create(
            from_account=validated_data.get('from_account'),
            to_account=validated_data.get("to_account"),
            user=user,
            note=validated_data.get('note'),
            event_date=validated_data.get('event_date'),
            transaction_type=validated_data.get('transaction_type'),
            category=validated_data.get('transaction_type_category'),
            amount=amount
        )

        transaction.save()
        return transaction

    def update(self, instance, validated_data):
        old_transaction = self.instance
        old_from_account = old_transaction.from_account
        old_to_account = old_transaction.to_account
        amount = old_transaction.amount
        if old_transaction.transaction_type.name == 'EXPENSE':
            old_from_account.balance += amount
            old_from_account.save()
        elif old_transaction.transaction_type.name == 'INCOME':
            old_to_account.balance -= amount
            old_to_account.save()
        elif old_transaction.transaction_type.name == 'TRANSFER':
            old_from_account.balance += amount
            old_from_account.save()
            old_to_account.balance -= amount
            old_to_account.save()

        # updating the balance now
        new_from_account = validated_data.get('from_account')
        new_to_account = validated_data.get('to_account')
        new_amount = validated_data.get('amount')
        new_transaction_type = validated_data.get('transaction_type')

        
        if new_transaction_type.name == 'EXPENSE':
            new_from_account.balance -= new_amount
            new_from_account.save()
        elif new_transaction_type.name == "INCOME":
            new_to_account.balance += new_amount
            new_to_account.save()
        elif new_transaction_type.name == "TRANSFER":
            new_from_account -= new_amount
            new_from_account.save()

            new_to_account.balance += new_amount
            new_to_account.save()

        # Updating the Transaction Model
        old_transaction.from_account = new_from_account
        old_transaction.to_account = new_to_account
        old_transaction.note = validated_data.get('note')
        old_transaction.amount = validated_data.get('amount')
        old_transaction.transaction_type = validated_data.get('transaction_type')
        old_transaction.category = validated_data.get('transaction_type_category')
        old_transaction.event_date = validated_data.get('event_date')

        old_transaction.save()
        return old_transaction


    def delete(self, validated_data):

        transaction = self.instance
        transaction_type = transaction.transaction_type
        amount = transaction.amount
        from_account = transaction.from_account
        to_account = transaction.to_account

        if transaction_type.name == 'EXPENSE':
            from_account.balance += amount
            from_account.save()

        elif transaction_type.name == 'INCOME':
            to_account.balance -= amount
            to_account.save()

        elif transaction_type.name == 'TRANSFER':
            from_account.balance += amount
            from_account.save()
            to_account.balance -= amount
            to_account.save()

        transaction.delete()
        return transaction






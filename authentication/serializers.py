from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(max_length=50, write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['email', "name",  "password", "password2"] 
        extra_kwargs = {
            'password': {"write_only": True}
        }

    def validate(self, attr):
        password = attr.get('password')
        password2 = attr.get("password2")

        if password != password2:
            raise serializers.ValidationError("Password does not match.")
        
        return attr
    
    def create(self, validated_data):
        password2 = validated_data.pop("password2")

        user = User.objects.create(
            email =  validated_data.get('email'),
            name = validated_data.get('name')
        )

        user.set_password(validated_data.get("password"))
        user.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(max_length=50, write_only=True)
    password2 = serializers.CharField(max_length=50, write_only=True)
    password = serializers.CharField(max_length=50, write_only=True)

    def validate(self, attr):
        user = self.context.get('user')
        password1 = attr.get('password1')
        password2 = attr.get('password2')

        if not user.check_password(attr.get('password')):
            raise serializers.ValidationError("Your current password is incorrect. Try angain!")
        
        if password1 != password2:
            raise serializers.ValidationError('Your new password and confirm password does not match')

        return attr
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('password1'))
        instance.save()
        return instance
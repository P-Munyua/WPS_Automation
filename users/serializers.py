# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['company', 'position', 'usage_count', 'last_activity']
        read_only_fields = ['usage_count', 'last_activity']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password', 'password2', 'country_code']
        extra_kwargs = {
            'email': {'required': False},
            'phone_number': {'required': False}
        }

    def validate(self, attrs):
        if not attrs.get('email') and not attrs.get('phone_number'):
            raise serializers.ValidationError("Either email or phone number must be provided.")

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'login_method', 'avatar_url', 
                 'country_code', 'is_verified', 'created_at', 'profile']
        read_only_fields = ['id', 'login_method', 'is_verified', 'created_at']
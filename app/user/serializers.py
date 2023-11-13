"""
Serializers for the user API View
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _
from core.models import QueueLogic

from rest_framework import serializers
from department.serializers import DepartmentSerializer




class UserBoardSerializer(serializers.ModelSerializer):
    """Serializer for the user list"""
    departments = DepartmentSerializer(many=True)
    task = serializers.StringRelatedField(source='tasks', many=True)    

    class Meta:
        model = get_user_model()
        fields = [
            'id', 'email',
            'username', 'first_name',
            'last_name', 'phone_number',
            'address', 'role', 'departments',
            'status', 'task'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'phone_number': {'required': False}
        }
    
    def to_representation(self, instance):
        response = super().to_representation(instance)
        number_of_task = QueueLogic.objects.filter(users__in=[response['id']], end=False).count()
        response['task'] = number_of_task
        return response


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    task = serializers.StringRelatedField(source='tasks', many=True)

    class Meta:
        model = get_user_model()
        fields = [
            'id', 'email', 'password',
            'username', 'first_name',
            'last_name', 'phone_number',
            'address', 'role', 'departments',
            'status', 'task'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'phone_number': {'required': False}
        }

    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user

    def to_representation(self, instance):
        response = super().to_representation(instance)
        number_of_task = QueueLogic.objects.filter(users__in=[response['id']], end=False).count()
        response['task'] = number_of_task
        return response


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )
        print(user)
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code="authorization")

        attrs['user'] = user
        return attrs


class UserManageSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name', 'role']


class UserNestedSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name']

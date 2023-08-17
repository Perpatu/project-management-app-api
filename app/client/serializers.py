"""
Serializers for Client APIs
"""
from rest_framework import serializers

from core.models import Client


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for client"""

    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['id']


class ClientNestedSerializer(serializers.ModelSerializer):
    """Serializer for client"""

    class Meta:
        model = Client
        fields = ['id', 'name']
        read_only_fields = ['id']

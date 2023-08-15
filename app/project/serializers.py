"""
Serializers for Project APIs
"""
from rest_framework import serializers

from core.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for project"""

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id']

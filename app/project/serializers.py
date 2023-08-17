"""
Serializers for Project APIs
"""
from rest_framework import serializers

from user.serializers import UserNestedSerializer
from client.serializers import ClientNestedSerializer

from core.models import (
    Project,
    CommentProject,
)


class CommentProjectSerializer(serializers.ModelSerializer):
    """Serializer for comment project"""

    class Meta:
        model = CommentProject
        fields = ['id', 'user', 'text', 'date_posted', 'read']
        read_only_fields = ['id', 'user', 'date_posted']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = {
            'id': UserNestedSerializer(instance.user).data['id'],
            'name': UserNestedSerializer(instance.user).data['name']
        }
        return response


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for project"""

    class Meta:
        model = Project
        fields = [
            'id',
            'manager',
            'client',
            'start',
            'deadline',
            'progress',
            'priority',
            'status',
            'number',
            'secretariat',
            'invoiced',
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['manager'] = {
            'id': UserNestedSerializer(instance.manager).data['id'],
            'name': UserNestedSerializer(instance.manager).data['name']
        }
        response['client'] = {
            'id': ClientNestedSerializer(instance.client).data['id'],
            'name': ClientNestedSerializer(instance.client).data['name']
        }
        return response


class ProjectDetailSerializer(ProjectSerializer):
    """Serializer for recipe detail view."""
    comments = CommentProjectSerializer(many=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['comments']

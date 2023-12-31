"""
Serializers for Project APIs
"""
from rest_framework import serializers

from user.serializers import UserNestedSerializer
from client.serializers import ClientNestedSerializer

from core.models import (
    Project,
    CommentProject,
    NotificationProject
)
from file.serializers import FileProjectSerializer


class CommentProjectDisplaySerializer(serializers.ModelSerializer):
    """Serializer for comment project"""

    class Meta:
        model = CommentProject
        fields = ['id', 'user', 'text', 'date_posted', 'read']
        read_only_fields = ['id', 'user', 'date_posted']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        first_name = UserNestedSerializer(instance.user).data['first_name']
        last_name = UserNestedSerializer(instance.user).data['last_name']
        response['user'] = {
            'id': UserNestedSerializer(instance.user).data['id'],
            'name': first_name[0].upper() + '. ' + last_name
        }
        return response


class CommentProjectManageSerializer(serializers.ModelSerializer):
    """Serializer Manage for comment project"""

    class Meta:
        model = CommentProject
        fields = ['id', 'user', 'project', 'text']
        read_only_fields = ['id']


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer create project"""

    class Meta:
        model = Project
        fields = [
            'id',
            'manager',
            'client',
            'start',
            'deadline',
            'priority',
            'progress',
            'name',
            'number',
            'order_number',
            'status',
        ]
        read_only_fields = ['id']
    def to_representation(self, instance):
        response = super().to_representation(instance)
        first_name = UserNestedSerializer(instance.manager).data['first_name']
        last_name = UserNestedSerializer(instance.manager).data['last_name']
        response['manager'] = {
            'id': UserNestedSerializer(instance.manager).data['id'],
            'name': first_name[0].upper() + '. ' + last_name
        }
        response['client'] = {
            'id': ClientNestedSerializer(instance.client).data['id'],
            'name': ClientNestedSerializer(instance.client).data['name'],
            'color': ClientNestedSerializer(instance.client).data['color'],
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
            'name',
            'number',
            'order_number',
            'secretariat',
            'invoiced',
            'company'
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        first_name = UserNestedSerializer(instance.manager).data['first_name']
        last_name = UserNestedSerializer(instance.manager).data['last_name']
        response['manager'] = {
            'id': UserNestedSerializer(instance.manager).data['id'],
            'name': first_name[0].upper() + '. ' + last_name
        }
        response['client'] = {
            'id': ClientNestedSerializer(instance.client).data['id'],
            'name': ClientNestedSerializer(instance.client).data['name'],
            'color': ClientNestedSerializer(instance.client).data['color'],
        }
        return response


class ProjectDetailSerializer(ProjectSerializer):
    """Serializer for project detail view."""
    comments = CommentProjectDisplaySerializer(many=True)
    files = FileProjectSerializer(many=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['comments', 'files']


class ProjectProgressSerializer(serializers.ModelSerializer):
    """Serializer for project"""

    class Meta:
        model = Project
        fields = ['id', 'progress', 'status']


class NotificationProjectSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTask"""

    class Meta:
        model = NotificationProject
        fields = '__all__'
        read_only_fields = ['id']

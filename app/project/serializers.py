"""
Serializers for Project APIs
"""
from rest_framework import serializers

from user.serializers import UserNestedSerializer
from client.serializers import ClientNestedSerializer

from core.models import (
    Project,
    CommentProject,
    File
)


def validate_file_extension(file_extension):
    allowed_extensions = ['pdf', 'dxf', 'xlsx', 'xls', 'txt', 'png',
                          'jpg', 'jpeg', 'rar', 'zip', 'doc', 'docx',
                          'igs', 'step', 'stp', 'stl']
    if file_extension in allowed_extensions:
        return True
    else:
        return False


class CommentProjectDisplaySerializer(serializers.ModelSerializer):
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


class CommentProjectManageSerializer(serializers.ModelSerializer):
    """Serializer Manage for comment project"""

    class Meta:
        model = CommentProject
        fields = ['id', 'user', 'project', 'text']
        read_only_fields = ['id']


class FilesUploadSerializer(serializers.ModelSerializer):
    """Serializer for upload file"""
    file = serializers.ListField(
        child=serializers.FileField(
            max_length=100000,
            allow_empty_file=False,
            use_url=False
        ))

    class Meta:
        model = File
        fields = '__all__'

        extra_kwargs = {
            'name': {'required': False},
        }

    def create(self, validated_data):
        project = validated_data['project']
        user = validated_data['user']
        destiny = validated_data['destiny']
        file = validated_data.pop('file')
        file_list = []

        for file in file:
            file_name_str = str(file).lower()
            file_split = file_name_str.split('.')
            file_extension = file_split[-1]
            if validate_file_extension(file_extension):
                file_obj = File.objects.create(
                    file=file, project=project, user=user,
                    destiny=destiny, name=file.name
                )
                fileurl = f'{file_obj.file.url}'
                file_list.append(fileurl)
            else:
                raise serializers.ValidationError('Wrong file format')
        return file_list


class FileSerializer(serializers.ModelSerializer):
    """Serializer for file"""
    class Meta:
        model = File
        fields = '__all__'


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
    comments = CommentProjectDisplaySerializer(many=True)
    files = FileSerializer(many=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['comments', 'files']

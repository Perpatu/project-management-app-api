"""
Serializers for files APIs
"""
from rest_framework import serializers

from core.models import (
    File,
    Project,
    CommentFile,
    QueueLogic
)
from user.serializers import UserNestedSerializer


def validate_file_extension(file_extension):
    allowed_extensions = ['pdf', 'dxf', 'xlsx', 'xls',
                          'txt', 'png', 'jpg', 'jpeg',
                          'rar', 'zip', 'doc', 'docx',
                          'igs', 'step', 'stp', 'stl',
                          'mkv', 'mp4',]
    if file_extension in allowed_extensions:
        return True
    else:
        return False


class FilesUploadSerializer(serializers.ModelSerializer):
    """Serializer for upload file"""
    file = serializers.ListField(
        child=serializers.FileField(
            max_length=10000000000000,
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
                fileurl = f'{file_obj.name}'
                file_list.append(fileurl)
            else:
                raise serializers.ValidationError('Wrong file format')
        return file_list


class CommentFileDisplaySerializer(serializers.ModelSerializer):
    """Serializer for comment project"""

    class Meta:
        model = CommentFile
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


class CommentFileManageSerializer(serializers.ModelSerializer):
    """Serializer Manage for comment file"""

    class Meta:
        model = CommentFile
        fields = ['id', 'user', 'file', 'text']
        read_only_fields = ['id']


class QueueLogicUpdateSerializer(serializers.ModelSerializer):
    """Serializer Manage for comment file"""

    class Meta:
        model = QueueLogic
        fields = '__all__'
        read_only_fields = ['id', 'project', 'department', 'file']


class QueueLogicManageSerializer(serializers.ModelSerializer):
    """Serializer for manage queue logic"""

    class Meta:
        model = QueueLogic
        fields = '__all__'
        read_only_fields = ['id']


class QueueLogicToFileSerializer(serializers.ModelSerializer):
    """Serializer for queue logic in File"""

    class Meta:
        model = QueueLogic
        exclude = ['file',]
        read_only_fields = ['id']


class FileProjectSerializer(serializers.ModelSerializer):
    """Serializer for file in project"""
    comments = CommentFileDisplaySerializer(many=True)
    queue = QueueLogicToFileSerializer(many=True)

    class Meta:
        model = File
        fields = ['id', 'name', 'file', 'comments', 'queue', 'destiny', 'new']
        read_only_fields = ['id']


class TestSerializer(serializers.ModelSerializer):
    """Serializer for file in project"""

    class Meta:
        model = File
        fields = ['departments',]


class ProjectFileSerializer(serializers.ModelSerializer):
    """Serializer for project"""

    class Meta:
        model = Project
        fields = ['id', 'manager']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        first_name = UserNestedSerializer(instance.manager).data['first_name']
        last_name = UserNestedSerializer(instance.manager).data['last_name']
        manager = first_name[0].upper() + '. ' + last_name
        response['manager'] = manager
        return response


class FileManageSerializer(serializers.ModelSerializer):
    """Serializer for manage file"""

    class Meta:
        model = File
        fields = ['id', 'name', 'file', 'destiny', 'queue']
        read_only_fields = ['id']


class FileDepartmentSerializer(serializers.ModelSerializer):
    """Serializer for file in department"""
    comments = CommentFileDisplaySerializer(many=True)
    queue = QueueLogicToFileSerializer(many=True)
    project = ProjectFileSerializer(many=False)

    class Meta:
        model = File
        fields = ['id', 'name', 'file', 'comments', 'project', 'queue']
        read_only_fields = ['id']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        dep_id = self.context.get('dep_id')
        filtered_queue = [
            queue_data for queue_data in response['queue']
            if queue_data['department'] == dep_id
        ]
        response['queue'] = filtered_queue
        return response

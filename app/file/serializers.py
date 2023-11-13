"""
Serializers for files APIs
"""
from rest_framework import serializers

from core.models import (
    File,
    Project,
    CommentFile,
    QueueLogic,
    NotificationTask
)
from user.serializers import UserNestedSerializer
from department.serializers import DepartmentSerializer


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
                if destiny == 'Secretariat':
                    file_new_list = file.name.split('.')
                    file_new_list[-2] = f"{file_new_list[-2]}_s"
                    file.name = '.'.join(file_new_list)
                    file_obj = File.objects.create(
                        file=file, project=project, user=user,
                        destiny=destiny, name=file.name
                    )
                elif destiny == 'Production':
                    file_obj = File.objects.create(
                        file=file, project=project, user=user,
                        destiny=destiny, name=file.name
                    )
                fileurl = f'{file_obj.name}'
                file_list.append(fileurl)
            else:
                raise serializers.ValidationError('Wrong file format')
        return file_list


class FileManageSerializer(serializers.ModelSerializer):
    """Serializer for manage file"""

    class Meta:
        model = File
        fields = ['id', 'name', 'file', 'destiny', 'queue']
        read_only_fields = ['id']


class CommentFileDisplaySerializer(serializers.ModelSerializer):
    """Serializer for comment project"""

    class Meta:
        model = CommentFile
        fields = ['id', 'user', 'text', 'file', 'date_posted', 'read']
        read_only_fields = ['id', 'user', 'date_posted']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        first_name = UserNestedSerializer(instance.user).data['first_name']
        last_name = UserNestedSerializer(instance.user).data['last_name']
        response['user'] = {
            'id': UserNestedSerializer(instance.user).data['id'],
            'name': first_name[0].upper() + '. ' + last_name
        }
        response['file'] = {
            'id': FileManageSerializer(instance.file).data['id'],
            'destiny': FileManageSerializer(instance.file).data['destiny']
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
    users = UserNestedSerializer(many=True)

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
        fields = [
            'id', 'name', 'file',
            'project', 'comments',
            'queue', 'destiny', 'new'
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['dep_id'] = []
        for q in response['queue']:
            response['dep_id'].append(q['department'])
        return response


class TestSerializer(serializers.ModelSerializer):
    """Serializer for file in project"""

    class Meta:
        model = File
        fields = ['departments',]


class ProjectFileSerializer(serializers.ModelSerializer):
    """Serializer for project"""

    class Meta:
        model = Project
        fields = ['id', 'manager', 'number']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        first_name = UserNestedSerializer(instance.manager).data['first_name']
        last_name = UserNestedSerializer(instance.manager).data['last_name']
        manager = first_name[0].upper() + '. ' + last_name
        response['manager'] = manager
        return response


class QueueLogicCalendarSerializer(serializers.ModelSerializer):
    """Serializer for task user in calendar"""

    project = ProjectFileSerializer(many=False)
    department = DepartmentSerializer(many=False)
    file = FileManageSerializer(many=False)

    class Meta:
        model = QueueLogic
        fields = [
            'id', 'file', 'department',
            'project', 'users', 'planned_start_date',
            'planned_end_date', 'start', 'paused', 'end'
        ]
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
        departments = [q['department'] for q in response['queue']]
        dep_index = departments.index(dep_id)

        filtered_queue = [
            {
                **queue_data,
                'next_task': next((q for q in response['queue'] if q['department'] > queue_data['department']), 'lack'),
                'prev_task': next((q for q in response['queue'] if q['department'] < queue_data['department']), 'lack')
            }
            for queue_data in response['queue']
            if queue_data['department'] == dep_id
        ]

        if filtered_queue:
            dep_index = departments.index(dep_id)
            if dep_index > 0:
                filtered_queue[0]['prev_task'] = next((q for q in response['queue'] if q['department'] == departments[dep_index - 1]), 'lack')
            if dep_index < len(departments) - 1:
                filtered_queue[0]['next_task'] = next((q for q in response['queue'] if q['department'] == departments[dep_index + 1]), 'lack')

        response['queue'] = filtered_queue
        return response


class NotificationTaskSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTask"""

    department = DepartmentSerializer(many=False)

    class Meta:
        model = NotificationTask
        fields = '__all__'
        read_only_fields = ['id']

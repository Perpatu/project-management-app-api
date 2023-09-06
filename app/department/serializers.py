"""
Serializers for department APIs
"""

from rest_framework import serializers

from core.models import Department, File, CommentFile, QueueLogic, Project
from user.serializers import UserNestedSerializer


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
            'name': first_name + ' ' + last_name
        }
        return response


class ProjectFileSerializer(serializers.ModelSerializer):
    """Serializer for project"""

    class Meta:
        model = Project
        fields = ['id', 'manager']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        first_name = UserNestedSerializer(instance.manager).data['first_name']
        last_name = UserNestedSerializer(instance.manager).data['last_name']
        manager = first_name + ' ' + last_name
        response['manager'] = manager
        return response


class QueueLogicToFileSerializer(serializers.ModelSerializer):
    """Serializer for queue logic in File"""

    class Meta:
        model = QueueLogic
        exclude = ['file',]
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
        dep_id = self.context.get('department_pk')
        #print(dep_id)
        response['queue'] = [queue_data for queue_data in response['queue'] if queue_data['department'] == 2]
        return response
    
class DepartmentDetailSerializer(serializers.ModelSerializer):
    """Serializer for Department"""
    files = FileDepartmentSerializer(many=True)
    class Meta:
        model = Department
        fields = ['id', 'name', 'order', 'files']
        read_only_fields = ['id']


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department"""

    class Meta:
        model = Department
        fields = ['id', 'name', 'order', 'files']
        read_only_fields = ['id']
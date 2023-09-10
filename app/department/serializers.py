"""
Serializers for department APIs
"""

from rest_framework import serializers

from core.models import Department, QueueLogic


class QueueLogicToFileSerializer(serializers.ModelSerializer):
    """Serializer for queue logic in File"""

    class Meta:
        model = QueueLogic
        exclude = ['file',]
        read_only_fields = ['id']


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department"""

    class Meta:
        model = Department
        fields = ['id', 'name', 'order']
        read_only_fields = ['id']


class DepartmentStatsSerializer(serializers.ModelSerializer):
    """Serializer for stats departments"""

    department = DepartmentSerializer(many=False)

    class Meta:
        model = QueueLogic
        fields = ['department',]

"""
Serializers for department APIs
"""

from rest_framework import serializers

from core.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department"""

    class Meta:
        model = Department
        fields = ['id', 'name', 'order']
        read_only_fields = ['id']
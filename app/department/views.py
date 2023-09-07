"""
Views for the department APIs.
"""

from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from core.models import (
    Department,
    QueueLogic,
)
from department import serializers
from file.serializers import DepartmentStatsSerializer


class DepartmentAdminViewSet(mixins.CreateModelMixin,
                             mixins.DestroyModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    """View for manage admin department APIs"""
    serializer_class = serializers.DepartmentSerializer
    queryset = Department.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        """Create a new department"""
        serializer.save()


class DepartmentAuthViewSet(mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    """View for auth users department APIs"""
    serializer_class = serializers.DepartmentDetailSerializer
    queryset = Department.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return DepartmentStatsSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == 'list':
            return QueueLogic.objects.all()
        return super().get_queryset()

    def retrieve(self, request, *args, **kwargs):
        """Returns a department with assinged files with queuelogic"""
        department = self.get_object()
        department_pk = department.pk
        response = super().retrieve(request, *args, **kwargs)
        data = response.data
        filter_data = data.copy()
        filter_data["files"] = []

        for file_data in data.get("files", []):
            filter_file = file_data.copy()
            filter_file["queue"] = [queue_data for queue_data in file_data.get(
                "queue", []) if queue_data.get("department") == department_pk]
            filter_data["files"].append(filter_file)
        return Response(filter_data)

    def list(self, request, *args, **kwargs):
        """Returns a list of how much files are assigned to department"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        department_counts = {}

        for item in data:
            department_name = item["department"]["name"]
            if department_name in department_counts:
                department_counts[department_name] += 1
            else:
                department_counts[department_name] = 1

        result = [
            {
                "quantity": count,
                "department": department_name
            } for department_name, count in department_counts.items()
        ]
        return Response(result)
